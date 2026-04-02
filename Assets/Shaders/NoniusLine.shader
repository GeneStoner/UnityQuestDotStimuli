Shader "Custom/NoniusLine"
{
    // Dichoptic nonius line.
    // _TargetEye: 0 = left eye only, 1 = right eye only, -1 = both eyes (binocular fallback).
    // Requires Multiview stereo rendering (m_StereoRenderingModeAndroid: 2) so that
    // unity_StereoEyeIndex is populated per-fragment. In Multipass mode (0) this always
    // returns 0 and dichoptic masking does not work — confirmed in prior testing.

    Properties
    {
        _Color     ("Color", Color) = (1,1,1,1)
        _TargetEye ("Target Eye (0=Left, 1=Right, -1=Both)", Int) = -1
    }

    SubShader
    {
        Tags
        {
            "RenderType"     = "Transparent"
            "Queue"          = "Transparent"
            "RenderPipeline" = "UniversalPipeline"
        }

        Blend SrcAlpha OneMinusSrcAlpha
        ZWrite Off
        Cull Off

        Pass
        {
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma multi_compile_instancing
            #pragma multi_compile _ STEREO_INSTANCING_ON
            #pragma multi_compile _ STEREO_MULTIVIEW_ON

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                UNITY_VERTEX_INPUT_INSTANCE_ID
                UNITY_VERTEX_OUTPUT_STEREO
            };

            CBUFFER_START(UnityPerMaterial)
                float4 _Color;
                int    _TargetEye;
            CBUFFER_END

            Varyings vert(Attributes input)
            {
                Varyings output;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_TRANSFER_INSTANCE_ID(input, output);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(output);
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                return output;
            }

            half4 frag(Varyings input) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(input);

                // Discard if this fragment is for the wrong eye.
                // _TargetEye == -1 means show to both eyes (binocular fallback).
                if (_TargetEye >= 0 && (int)unity_StereoEyeIndex != _TargetEye)
                    discard;

                return half4(_Color.rgb, _Color.a);
            }
            ENDHLSL
        }
    }

    // Fallback for non-URP / editor preview
    SubShader
    {
        Tags { "RenderType" = "Transparent" "Queue" = "Transparent" }
        Blend SrcAlpha OneMinusSrcAlpha
        ZWrite Off
        Cull Off
        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"
            struct appdata { float4 vertex : POSITION; };
            struct v2f    { float4 pos : SV_POSITION; };
            float4 _Color;
            v2f vert(appdata v) { v2f o; o.pos = UnityObjectToClipPos(v.vertex); return o; }
            fixed4 frag(v2f i) : SV_Target { return fixed4(_Color.rgb, _Color.a); }
            ENDCG
        }
    }
}
