"""
verify_payloads.py — close the loop on reconstruction correctness.

Requires a session TSV built with writeTrajectoryPayloads=true (the new default).
For every trial, it:
  1. Reconstructs motionKindByFrame from logged params
  2. Compares the reconstructed payload string directly against the logged payload string
  3. Confirms FNV1a32 of both match MkHash32

Run after: rebuild Unity → run NMoCol session on headset → adb pull → copy TSV to Agents/Data/

Usage:
    python3 verify_payloads.py <session_id>
    e.g. python3 verify_payloads.py 260515_1234
"""

import sys, os, pandas as pd, numpy as np

MK_CW=1; MK_CCW=2; MK_LIN=3; MK_NC=4

def build_mk_payload(row):
    N=int(row.TotalFrames); tStart=int(row.TransStartFrame); tEnd=int(row.TransEndFrame)
    swap=str(row.SwapType); cond=str(row.Cond); rot=int(row.RotCfg)
    motion_swap=swap in('M','MC'); is_cued=(cond=='CUED')
    aRot=MK_CW if rot==0 else MK_CCW
    bRot=MK_CCW if rot==0 else MK_CW
    mk=np.zeros((4,N),dtype=int)
    for f in range(N):
        after_swap=f>=tStart
        cA=bRot if(motion_swap and after_swap) else aRot
        cB=aRot if(motion_swap and after_swap) else bRot
        mk[0,f]=cA; mk[1,f]=cA; mk[2,f]=cB; mk[3,f]=cB
    for f in range(max(0,tStart),min(N,tEnd)):
        if is_cued:  mk[2,f]=MK_LIN; mk[3,f]=MK_NC
        else:        mk[0,f]=MK_LIN; mk[1,f]=MK_NC
    return ';'.join('|'.join(str(mk[sf,f]) for sf in range(4)) for f in range(N))

def fnv1a32(s):
    h=2166136261
    for c in s.encode('utf-8'): h^=c; h=(h*16777619)&0xFFFFFFFF
    return h

if len(sys.argv)<2:
    print("Usage: python3 verify_payloads.py <session_id>  e.g. 260515_1234")
    sys.exit(1)

sess=sys.argv[1]
DATA=os.path.join(os.path.dirname(__file__),'../../Data')
tsv=os.path.join(DATA,f'vr_dots_session_{sess}.tsv')
if not os.path.exists(tsv):
    print(f"File not found: {tsv}")
    sys.exit(1)

df=pd.read_csv(tsv,sep='\t')
df=df[df['RespDeg']>=0].reset_index(drop=True)

# Check if payloads are present
if df['MotionTypeByFrame_SubfieldCodes'].isna().all():
    print("ERROR: MotionTypeByFrame_SubfieldCodes is all NaN.")
    print("This session was built with writeTrajectoryPayloads=false.")
    print("Rebuild Unity (writeTrajectoryPayloads=true is now the default) and run a new session.")
    sys.exit(1)

print(f"Session {sess}: {len(df)} trials, payloads present.")
print()

passed=0; failed=0; hash_ok=0

for i,row in df.iterrows():
    reconstructed=build_mk_payload(row)
    logged=str(row.MotionTypeByFrame_SubfieldCodes)
    hash_logged=int(row.MkHash32,16)
    hash_reconstructed=fnv1a32(reconstructed)
    hash_logged_payload=fnv1a32(logged)

    payload_match = (reconstructed==logged)
    hash_match    = (hash_reconstructed==hash_logged)
    hash_logged_valid = (hash_logged_payload==hash_logged)

    if payload_match and hash_match:
        passed+=1
    else:
        failed+=1
        print(f"Trial {i:3d}  swap={row.SwapType:4s}  cond={row.Cond:6s}  rot={row.RotCfg}:")
        if not payload_match:
            r_parts=reconstructed.split(';')
            l_parts=logged.split(';')
            diffs=[(f,r_parts[f],l_parts[f]) for f in range(min(len(r_parts),len(l_parts))) if r_parts[f]!=l_parts[f]]
            print(f"  Payload mismatch: {len(diffs)} frame(s) differ")
            for fr,rp,lp in diffs[:3]:
                print(f"    frame {fr}: reconstructed={rp}  logged={lp}")
        if not hash_match:
            print(f"  Hash mismatch: reconstructed={hash_reconstructed:08X}  logged={hash_logged:08X}")
        if not hash_logged_valid:
            print(f"  WARNING: logged hash doesn't match logged payload — data corruption?")

print(f"\n{'='*50}")
print(f"Payload match:   {passed}/{passed+failed} trials PASS")
if failed==0:
    print("Motion-kind reconstruction is EXACT for all trials.")
    print("Dot position reconstruction (DotNetRandom port) is the remaining unverified step.")
    print("To verify positions, add per-frame XY logging to StimulusBuilder.cs.")
else:
    print(f"FAIL: {failed} trials have payload mismatches. Review output above.")
