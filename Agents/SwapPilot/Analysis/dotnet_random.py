"""
dotnet_random.py — Python port of System.Random from Mono/.NET Framework 4.x

Implements Knuth's subtractive generator exactly as used by Unity (Mono runtime).
This matches the .NET Framework reference source, not .NET Core 6+ (which changed
the algorithm). Unity uses Mono, which follows the .NET Framework implementation.

Reference:
  https://github.com/microsoft/referencesource/blob/master/mscorlib/system/random.cs

Usage:
    rng = DotNetRandom(seed)
    x   = rng.next_double()   # float in [0.0, 1.0)
    n   = rng.next_int()      # non-negative int in [0, 2^31-1)

Verification:
    Run verify_rng.py to compare output against known vectors from the Unity APK.
"""

import ctypes

_MBIG  = 2_147_483_647   # Int32.MaxValue
_MSEED = 161_803_398
_MZ    = 0


class DotNetRandom:
    """
    Exact Python port of System.Random(int seed) from Mono/.NET Framework 4.x.
    Only next_double() and next_int() are implemented — the two methods used by
    VRDots StimulusBuilder (UniformAnnulus draws two NextDouble() per dot;
    HandleOutOfBounds / ReplotSubfield each create a fresh instance and draw two).
    """

    __slots__ = ('_inext', '_inextp', '_seed_array')

    def __init__(self, seed: int):
        # Replicate C# int32 truncation of the seed parameter
        seed = ctypes.c_int32(seed).value

        seed_array = [0] * 56
        subtraction = _MBIG if seed == -2_147_483_648 else abs(seed)
        mj = _MSEED - subtraction
        seed_array[55] = mj
        mk = 1

        ii = 0
        for i in range(1, 55):
            ii += 21
            if ii >= 55:
                ii -= 55
            seed_array[ii] = mk
            mk = mj - mk
            if mk < 0:
                mk += _MBIG
            mj = seed_array[ii]

        for _ in range(1, 5):
            for i in range(1, 56):
                n = i + 30
                if n >= 55:
                    n -= 55
                # Use int32-wrapped subtraction to match C# overflow semantics.
                # Matters when seed_array[55] (= initial mj) is negative, turning
                # subtraction into addition that can exceed int32 max.
                v = ctypes.c_int32(seed_array[i] - seed_array[1 + n]).value
                if v < 0:
                    v += _MBIG
                seed_array[i] = v

        self._inext  = 0
        self._inextp = 21
        self._seed_array = seed_array

    def _internal_sample(self) -> int:
        loc_inext  = self._inext  + 1
        loc_inextp = self._inextp + 1
        if loc_inext  >= 56: loc_inext  = 1
        if loc_inextp >= 56: loc_inextp = 1

        ret_val = self._seed_array[loc_inext] - self._seed_array[loc_inextp]
        if ret_val == _MBIG: ret_val -= 1
        if ret_val < 0:      ret_val += _MBIG

        self._seed_array[loc_inext] = ret_val
        self._inext  = loc_inext
        self._inextp = loc_inextp
        return ret_val

    def next_double(self) -> float:
        """Equivalent to C# NextDouble(). Returns float in [0.0, 1.0)."""
        return self._internal_sample() * (1.0 / _MBIG)

    def next_int(self) -> int:
        """Equivalent to C# Next(). Returns non-negative int in [0, Int32.MaxValue)."""
        return self._internal_sample()


# ── Convenience: UniformAnnulus matching StimulusBuilder.cs ───────────────────

import math

def uniform_annulus(rng: DotNetRandom, r_out: float, r_in: float):
    """
    Matches StimulusBuilder.UniformAnnulus(rng, R_out, R_in).
    Returns (x, y) in meters (same units as the builder).
    Falls back to UniformDisk when r_in <= 0 or r_in >= r_out.
    Consumes exactly 2 NextDouble() calls.
    """
    if r_in <= 0.0 or r_in >= r_out:
        # UniformDisk
        u  = rng.next_double()
        r  = r_out * math.sqrt(u)
        th = rng.next_double() * (2.0 * math.pi)
    else:
        u  = rng.next_double()
        r  = math.sqrt(u * (r_out**2 - r_in**2) + r_in**2)
        th = rng.next_double() * (2.0 * math.pi)
    return r * math.cos(th), r * math.sin(th)


def dot_net_hash(seed_base: int, dot_index: int, frame: int) -> int:
    """
    Matches StimulusBuilder.Hash(seedBase, dotIndex, frame).
    Returns a 32-bit signed int (as Python int).
    """
    h = ctypes.c_int32(17).value
    h = ctypes.c_int32(h * 31 + seed_base).value
    h = ctypes.c_int32(h * 31 + dot_index).value
    h = ctypes.c_int32(h * 31 + frame).value
    return h if h != 0 else 1
