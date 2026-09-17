Shader "Custom/DotScreenSpaceFixed"
{
    // Fixed-AA version of DotScreenSpace. Identical except the fragment shader
    // uses a constant aaW = 0.03 instead of fwidth(dist)*1.5.
    //
    // The adaptive fwidth path makes aaW ≈ 0.75 for a 2-pixel dot (Quest 3 at
    // 0.08°), eliminating any solid core and causing luminance to swing with
    // sub-pixel position. The fixed value keeps the core fully saturated and
    // the edge transition narrow and stable.
    //
    // To compare: assign this shader to the dot material in StimulusBuilder's
    // Inspector alongside the original DotScreenSpace shader.

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

        Blend One One      // additive: no occlusion ordering, colors summate
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
                float4 positionOS : POSITION;
                float2 uv         : TEXCOORD0;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv         : TEXCOORD0;
                UNITY_VERTEX_OUTPUT_STEREO
            };

            CBUFFER_START(DotPerRenderer)
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

                float eyeSign = (unity_StereoEyeIndex == 0) ? 1.0 : -1.0;

                float3 centre = _WorldCenter.xyz
                              + _RightDir.xyz * (eyeSign * _HalfDisparityWorld);

                float3 worldPos = centre
                    + _RightDir.xyz * (input.positionOS.x * 2.0 * _HalfSizeMeters)
                    + _UpDir.xyz    * (input.positionOS.y * 2.0 * _HalfSizeMeters);

                output.positionCS = TransformWorldToHClip(worldPos);
                output.uv = input.uv;
                return output;
            }

            half4 frag(Varyings input) : SV_Target
            {
                UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(input);

                float2 c    = input.uv - 0.5;
                float  dist = length(c);
                // Fixed AA width — stable luminance regardless of sub-pixel position.
                // fwidth(dist)*1.5 ≈ 0.75 for a 2-pixel dot, which eliminates the
                // solid core entirely. 0.03 keeps the core fully saturated.
                float  aaW   = 0.03;
                float  alpha = (1.0 - smoothstep(0.5 - aaW, 0.5 + aaW, dist)) * _Color.a;

                return half4(_Color.rgb, alpha);
            }
            ENDHLSL
        }
    }
}
