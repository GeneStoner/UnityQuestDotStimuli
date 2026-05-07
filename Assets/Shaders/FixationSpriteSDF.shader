Shader "Custom/FixationSpriteSDF"
{
    // Analytical SDF bullseye — resolution-independent, no texture needed.
    // Geometry parameters are passed as material properties from Fixation_Controller.cs.
    // All distances are in UV space with center at (0.5, 0.5); outer disc radius = 0.5.
    //
    // Queue=Overlay+20, ZTest Always — always renders on top of dots (Overlay+10).
    //
    // ROLLBACK: In Fixation_Controller Inspector, uncheck "Use SDF Shader" to revert
    // to the texture-based FixationSprite path.

    Properties
    {
        // Normalized to UV half-space: 0.0 = center, 0.5 = outer disc edge
        _CrossHalfWNorm   ("Cross half-width (norm)", Float) = 0.069
        _DotRadiusNorm    ("Center dot radius (norm)", Float) = 0.056
        _CrossOvershootNorm ("Cross tip overshoot beyond disc (norm)", Float) = 0.028
        _FixColor         ("Disc + dot color", Color) = (1,1,1,1)
        _CrossColor       ("Crosshair color", Color) = (0,0,0,1)
    }

    SubShader
    {
        Tags
        {
            "RenderType"     = "Transparent"
            "Queue"          = "Overlay+20"
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

            CBUFFER_START(UnityPerMaterial)
                float  _CrossHalfWNorm;
                float  _DotRadiusNorm;
                float  _CrossOvershootNorm;
                float4 _FixColor;
                float4 _CrossColor;
            CBUFFER_END

            Varyings vert(Attributes input)
            {
                Varyings output;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(output);
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.uv = input.uv;
                return output;
            }

            half4 frag(Varyings input) : SV_Target
            {
                UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(input);

                float2 p = input.uv - 0.5;   // centered coords [-0.5, 0.5]
                float  r = length(p);

                // fwidth gives the screen-space derivative (~1 px in normalized units).
                // Used as the AA transition width for all edges — true 1-pixel AA.
                float aa = fwidth(r);

                // --- Disc (radius = 0.5) ---
                float discMask = 1.0 - smoothstep(0.5 - aa, 0.5 + aa, r);

                // --- Extended clip for cross tips (_CrossOvershootNorm beyond disc edge) ---
                float extR    = 0.5 + _CrossOvershootNorm;
                float extMask = 1.0 - smoothstep(extR - aa, extR + aa, r);

                // --- Cross arms (unclipped strips; clipping applied below) ---
                float hArm    = 1.0 - smoothstep(_CrossHalfWNorm - aa, _CrossHalfWNorm + aa, abs(p.y));
                float vArm    = 1.0 - smoothstep(_CrossHalfWNorm - aa, _CrossHalfWNorm + aa, abs(p.x));
                float crossMask = max(hArm, vArm);   // no disc clip yet

                // --- Center dot ---
                float dotMask = 1.0 - smoothstep(_DotRadiusNorm - aa, _DotRadiusNorm + aa, r);

                // --- Porter-Duff composite ---
                // Start fully transparent (black × 0 alpha).
                half3 rgb   = (half3)0;
                float alpha = 0.0;

                // Layer 1: white disc
                rgb   = lerp(rgb,  _FixColor.rgb,  discMask);
                alpha = lerp(alpha, 1.0,            discMask);

                // Layer 2: black cross clipped to disc interior
                float crossInDisc = crossMask * discMask;
                rgb = lerp(rgb, _CrossColor.rgb, crossInDisc);

                // Layer 3: white center dot (over cross intersection)
                rgb = lerp(rgb, _FixColor.rgb, dotMask);

                // Layer 4: cross tips that extend slightly beyond disc edge.
                // rgb outside disc is already black (init=0); crossColor is black,
                // so lerp is correct even for non-black crossColor.
                float crossExt = crossMask * extMask * (1.0 - discMask);
                alpha = max(alpha, crossExt);
                rgb   = lerp(rgb, _CrossColor.rgb, crossExt);

                return half4(rgb, alpha);
            }
            ENDHLSL
        }
    }
}
