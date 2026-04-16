Shader "Custom/DotScreenSpace"
{
    // Screen-space stereo dot shader (Solution A).
    //
    // Each dot is a billboard quad whose corners are computed in WORLD SPACE from
    // the stimulus plane's right/up vectors, then projected per-eye via Unity's
    // standard TransformWorldToHClip.  This means:
    //   - Correct stereo rendering in single-pass instanced mode on Quest
    //   - No clip-space hacks, no axis-alignment sensitivity
    //   - Depth encoded as a tiny per-eye world-space shift (_HalfDisparityWorld)
    //     rather than a world-space z-offset, so ApplyDepthOffsets is bypassed
    //
    // Per-dot properties set via MaterialPropertyBlock each frame:
    //   _WorldCenter          float4   Dot center in world space (xyz)
    //   _RightDir             float4   Stimulus plane right vector (xyz)
    //   _UpDir                float4   Stimulus plane up vector (xyz)
    //   _HalfSizeMeters       float    Half the dot diameter in world-space metres
    //   _HalfDisparityWorld   float    Per-eye horizontal shift in world-space metres
    //                                  positive = uncrossed / Far
    //                                  negative = crossed  / Near
    //                                  left eye adds +value, right eye adds -value
    //
    // Per-subfield (shared material):
    //   _Color                float4   RGBA colour

    Properties
    {
        _Color              ("Color",                         Color)  = (1,1,1,1)
        _WorldCenter        ("World Center (xyz)",            Vector) = (0,0,2,0)
        _RightDir           ("Stimulus Plane Right (xyz)",    Vector) = (1,0,0,0)
        _UpDir              ("Stimulus Plane Up (xyz)",       Vector) = (0,1,0,0)
        _HalfSizeMeters     ("Half Size (metres)",            Float)  = 0.01
        _HalfDisparityWorld ("Signed Half Disparity (metres)",Float)  = 0.0
    }

    SubShader
    {
        Tags
        {
            "RenderType"     = "Transparent"
            "Queue"          = "Overlay+10"
            "RenderPipeline" = "UniversalPipeline"
        }

        Blend SrcAlpha OneMinusSrcAlpha
        ZWrite Off
        ZTest  Always
        Cull   Off

        Pass
        {
            HLSLPROGRAM
            #pragma vertex   vert
            #pragma fragment frag
            #pragma multi_compile_instancing
            #pragma multi_compile __ UNITY_SINGLE_PASS_STEREO STEREO_INSTANCING_ON STEREO_MULTIVIEW_ON

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;  // quad local xy in [-0.5, +0.5]
                float2 uv         : TEXCOORD0; // [0,1] × [0,1]
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv         : TEXCOORD0;
                UNITY_VERTEX_OUTPUT_STEREO
            };

            CBUFFER_START(UnityPerMaterial)
                float4 _Color;
                float4 _WorldCenter;
                float4 _RightDir;
                float4 _UpDir;
                float  _HalfSizeMeters;
                float  _HalfDisparityWorld;
            CBUFFER_END

            Varyings vert(Attributes input)
            {
                Varyings output;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(output);

                // Left eye (+1) shifts right for Far (uncrossed) disparity.
                // Right eye (-1) shifts left for Far disparity.
                float eyeSign = (unity_StereoEyeIndex == 0) ? 1.0 : -1.0;

                // Billboard: place quad corners in world space around the dot centre,
                // shifted per-eye for the disparity.
                float3 centre = _WorldCenter.xyz
                              + _RightDir.xyz * (eyeSign * _HalfDisparityWorld);

                float3 worldPos = centre
                    + _RightDir.xyz * (input.positionOS.x * 2.0 * _HalfSizeMeters)
                    + _UpDir.xyz    * (input.positionOS.y * 2.0 * _HalfSizeMeters);

                // Standard per-eye projection — correct stereo on Quest.
                output.positionCS = TransformWorldToHClip(worldPos);
                output.uv = input.uv;
                return output;
            }

            half4 frag(Varyings input) : SV_Target
            {
                UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(input);

                // Smooth anti-aliased circle in UV space.
                float2 c    = input.uv - 0.5;
                float  dist = length(c);
                float  aaW  = max(0.01, fwidth(dist) * 1.5);
                float  alpha = (1.0 - smoothstep(0.5 - aaW, 0.5 + aaW, dist)) * _Color.a;

                return half4(_Color.rgb, alpha);
            }
            ENDHLSL
        }
    }
}
