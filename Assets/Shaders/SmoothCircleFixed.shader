Shader "Custom/SmoothCircleFixed"
{
    // Fixed-AA version of SmoothCircle. The original uses max(_Smoothness,
    // fwidth(dist)*1.5) which, for a 2-pixel dot on Quest 3, yields aaWidth≈0.75
    // — the entire dot becomes a soft gradient with no solid core, and total
    // luminance varies with sub-pixel position.
    //
    // Here aaWidth = _Smoothness only (default 0.03). The Inspector slider still
    // lets you tune edge softness; fwidth is not used. Dot cores are fully
    // saturated and luminance is stable across sub-pixel positions.

    Properties
    {
        _Color ("Color", Color) = (1,1,1,1)
        _InnerRadius ("Inner Radius (0-1)", Range(0, 1)) = 0.0
        _OuterRadius ("Outer Radius (0-1)", Range(0, 1)) = 0.5
        _Smoothness ("Edge Smoothness (fixed AA width)", Range(0.001, 0.1)) = 0.03
    }

    SubShader
    {
        Tags
        {
            "RenderType" = "Transparent"
            "Queue" = "Transparent"
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

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                float2 uv : TEXCOORD0;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            CBUFFER_START(UnityPerMaterial)
                float4 _Color;
                float _InnerRadius;
                float _OuterRadius;
                float _Smoothness;
            CBUFFER_END

            Varyings vert(Attributes input)
            {
                Varyings output;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_TRANSFER_INSTANCE_ID(input, output);

                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.uv = input.uv;
                return output;
            }

            half4 frag(Varyings input) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);

                float2 centered = input.uv - 0.5;
                float dist = length(centered);

                // Fixed AA — no fwidth. Inspector _Smoothness controls edge width.
                float aaWidth = _Smoothness;

                float outerAlpha = 1.0 - smoothstep(_OuterRadius - aaWidth, _OuterRadius + aaWidth, dist);
                float innerAlpha = smoothstep(_InnerRadius - aaWidth, _InnerRadius + aaWidth, dist);

                float alpha = outerAlpha * innerAlpha * _Color.a;
                return half4(_Color.rgb, alpha);
            }
            ENDHLSL
        }
    }

    SubShader
    {
        Tags
        {
            "RenderType" = "Transparent"
            "Queue" = "Transparent"
        }

        Blend SrcAlpha OneMinusSrcAlpha
        ZWrite Off
        Cull Off

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag

            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct v2f
            {
                float4 pos : SV_POSITION;
                float2 uv : TEXCOORD0;
            };

            float4 _Color;
            float _InnerRadius;
            float _OuterRadius;
            float _Smoothness;

            v2f vert(appdata v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                o.uv = v.uv;
                return o;
            }

            fixed4 frag(v2f i) : SV_Target
            {
                float2 centered = i.uv - 0.5;
                float dist = length(centered);

                float aaWidth = _Smoothness;

                float outerAlpha = 1.0 - smoothstep(_OuterRadius - aaWidth, _OuterRadius + aaWidth, dist);
                float innerAlpha = smoothstep(_InnerRadius - aaWidth, _InnerRadius + aaWidth, dist);

                float alpha = outerAlpha * innerAlpha * _Color.a;
                return fixed4(_Color.rgb, alpha);
            }
            ENDCG
        }
    }
}
