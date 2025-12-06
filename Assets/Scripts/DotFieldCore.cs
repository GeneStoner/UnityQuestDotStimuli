using System;
using UnityEngine;

namespace Stim
{
    /// <summary>
    /// Pure core: generates/updates dot positions inside a circular aperture.
    /// * No Unity lifecycle
    /// * No materials, meshes, input, or phases
    /// </summary>
    public class DotFieldCore
    {
        public Vector2[] PosA { get; private set; }
        public Vector2[] PosB { get; private set; }

        public float ApertureRadiusM { get; private set; }  // meters
        public float SpeedMps { get; private set; }         // meters/sec for linear

        private System.Random _rngA, _rngB;

        public void Configure(float apertureDeg, float viewDistM, int nA, int nB, int seed, float speedDegPerSec)
        {
            ApertureRadiusM = Mathf.Max(1e-5f, DegToMeters(apertureDeg, viewDistM) * 0.5f);
            SpeedMps        = DegToMeters(speedDegPerSec, viewDistM);
            PosA = new Vector2[Mathf.Max(1, nA)];
            PosB = new Vector2[Mathf.Max(1, nB)];
            _rngA = new System.Random(seed);
            _rngB = new System.Random(seed + 99991);
        }

        public void GeneratePositions()
        {
            if (PosA == null || PosB == null) return;
            for (int i = 0; i < PosA.Length; i++) PosA[i] = UniformDisk(_rngA, ApertureRadiusM);
            for (int i = 0; i < PosB.Length; i++) PosB[i] = UniformDisk(_rngB, ApertureRadiusM);
        }

        // Optional “engine” steps (you can ignore if you only want static layouts)
        public void StepRotation(Vector2[] pos, float dt, float omegaDegPerSec, int dir)
        {
            if (pos == null) return;
            float w = omegaDegPerSec * Mathf.Deg2Rad * Mathf.Sign(dir == 0 ? 1 : dir);
            float c = Mathf.Cos(w * dt), s = Mathf.Sin(w * dt);
            float R = ApertureRadiusM;
            for (int i = 0; i < pos.Length; i++)
            {
                float x = pos[i].x, y = pos[i].y;
                pos[i].x = x * c - y * s;
                pos[i].y = x * s + y * c;
                float mag = pos[i].magnitude;
                if (mag > R) pos[i] *= 0.999f * (R / mag);
            }
        }

        public void StepLinear(Vector2[] pos, Vector2[] vel, float dt)
        {
            if (pos == null || vel == null) return;
            float R = ApertureRadiusM;
            for (int i = 0; i < pos.Length; i++)
            {
                Vector2 p = pos[i] + vel[i] * dt;
                float mag = p.magnitude;
                if (mag > R)
                {
                    Vector2 n = p / Mathf.Max(1e-6f, mag);
                    p -= n * (2f * R);
                    p *= 0.999f;
                }
                pos[i] = p;
            }
        }

        public static float DegToMeters(float deg, float viewDistM)
            => 2f * viewDistM * Mathf.Tan(0.5f * Mathf.Deg2Rad * Mathf.Max(0f, deg));

        private static Vector2 UniformDisk(System.Random rng, float R)
        {
            float u = (float)rng.NextDouble();
            float r = R * Mathf.Sqrt(u);
            float th = (float)rng.NextDouble() * (2f * Mathf.PI);
            return new Vector2(r * Mathf.Cos(th), r * Mathf.Sin(th));
        }
    }
}