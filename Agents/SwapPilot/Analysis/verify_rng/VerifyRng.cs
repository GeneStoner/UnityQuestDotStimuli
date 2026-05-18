// VerifyRng.cs — run with: dotnet script VerifyRng.cs  (or csc + mono)
// Prints the first 20 NextDouble() outputs for a set of seeds.
// Compare against verify_rng.py to confirm the Python DotNetRandom port is exact.
using System;

class VerifyRng
{
    static void Main()
    {
        int[] seeds = { 0, 1, 42, -1, 12345, 999999999, -2147483648 };
        int N = 20;

        foreach (int seed in seeds)
        {
            var rng = new Random(seed);
            Console.Write($"seed={seed,12}: ");
            for (int i = 0; i < N; i++)
            {
                double v = rng.NextDouble();
                Console.Write($"{v:R}");
                if (i < N - 1) Console.Write(",");
            }
            Console.WriteLine();
        }
    }
}
