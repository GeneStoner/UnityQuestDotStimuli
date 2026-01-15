Shader "Custom/SmoothCircle"
{
    Properties
    {
        _Color ("Color", Color) = (1,1,1,1)
        _InnerRadius ("Inner Radius (0-1)", Range(0, 1)) = 0.0
        _OuterRadius ("Outer Radius (0-1)", Range(0, 1)) = 0.5
        _Smoothness ("Edge Smoothness", Range(0.001, 0.1)) = 0.01
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

                // Center UV at (0,0), range becomes -0.5 to 0.5
                float2 centered = input.uv - 0.5;
                float dist = length(centered);

                // Calculate screen-space anti-aliasing width using derivatives
                // fwidth gives us how much 'dist' changes per pixel - perfect for AA
                float pixelWidth = fwidth(dist);
                // Use larger of manual smoothness or 1.5 pixels worth
                float aaWidth = max(_Smoothness, pixelWidth * 1.5);

                // Anti-aliased circle using smoothstep
                // Outer edge: fade from 1 to 0 as dist approaches OuterRadius
                float outerAlpha = 1.0 - smoothstep(_OuterRadius - aaWidth, _OuterRadius + aaWidth, dist);

                // Inner edge (for rings): fade from 0 to 1 as dist moves past InnerRadius
                float innerAlpha = smoothstep(_InnerRadius - aaWidth, _InnerRadius + aaWidth, dist);

                // Combine: visible where outside inner AND inside outer
                float alpha = outerAlpha * innerAlpha * _Color.a;

                // For filled circle (InnerRadius = 0), innerAlpha is always 1
                return half4(_Color.rgb, alpha);
            }
            ENDHLSL
        }
    }

    // Fallback for non-URP
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

                // Screen-space AA using derivatives
                float pixelWidth = fwidth(dist);
                float aaWidth = max(_Smoothness, pixelWidth * 1.5);

                float outerAlpha = 1.0 - smoothstep(_OuterRadius - aaWidth, _OuterRadius + aaWidth, dist);
                float innerAlpha = smoothstep(_InnerRadius - aaWidth, _InnerRadius + aaWidth, dist);

                float alpha = outerAlpha * innerAlpha * _Color.a;

                return fixed4(_Color.rgb, alpha);
            }
            ENDCG
        }
    }
}
