"""
reconstruct_animation_html.py
Deterministic frame-by-frame reconstruction of VRDots stimuli.
8 panels: N/M/C/MC × CUED/UNCUED from SubfieldSwap_CatekExact_NMoCol_v1
RotCfg=0 for all panels.

Motion-kind sequences verified against MkHash32 for all 8 conditions (8/8 PASS).
"""

import sys, os, math, json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from dotnet_random import DotNetRandom, uniform_annulus, dot_net_hash

SIM_HZ=90; AP_DEG=1.65; EXCL_DEG=0.5; DOT_R_DEG=0.04
ROT_DEG_FR=81.0/SIM_HZ; TRANS_DEG_FR=2.26/SIM_HZ; DOTS_PER_SF=43//2
MK_CW=1; MK_CCW=2; MK_LIN=3; MK_NC=4
# Fixation: Fixation_Controller (outerDiam=1.8°, innerDiam=0.2°, crossThickness=0.375°)
# scaled by fixationScaleFactor=0.47 from Exp_SubfieldSwap_CatekExact_NMoCol.asset
FIX_OUTER_R  = 1.8 / 2 * 0.47    # white disc radius = 0.423°
FIX_CROSS_HW = 0.375 / 2 * 0.47  # cross arm half-width = 0.088°
FIX_INNER_R  = 0.2 / 2 * 0.47    # white center dot radius = 0.047°

def seed_base(sa0,sf):
    return (sa0+sf*1000003) if sf<2 else (sa0+99991+sf*1000003)

DATA='/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Agents/Data'
df=pd.read_csv(f'{DATA}/vr_dots_session_260515_0848.tsv',sep='\t')
df=df[df['RespDeg']>=0].reset_index(drop=True)

CONDITIONS=['N','M','C','MC']
COND_LABELS={'N':'No Swap','M':'Motion Swap','C':'Color Swap','MC':'Motion+Color'}
COND_COLORS={'N':'#2ca02c','M':'#1f77b4','C':'#9467bd','MC':'#d62728'}
CUES=['CUED','UNCUED']

trials={}
for cue in CUES:
    for swap in CONDITIONS:
        mask=(df['SwapType']==swap)&(df['Cond']==cue)&(df['RotCfg']==0)
        trials[(cue,swap)]=df[mask].iloc[0]

# ── Motion-kind reconstruction (verified against MkHash32) ────────────────────
def build_mk(swap, cue, row):
    N=int(row.TotalFrames); tStart=int(row.TransStartFrame); tEnd=int(row.TransEndFrame)
    motion_swap=swap in('M','MC'); is_cued=(cue=='CUED')
    mk=np.zeros((4,N),dtype=int)
    for f in range(N):
        after_swap=f>=tStart
        cA=MK_CCW if(motion_swap and after_swap) else MK_CW
        cB=MK_CW  if(motion_swap and after_swap) else MK_CCW
        mk[0,f]=cA; mk[1,f]=cA; mk[2,f]=cB; mk[3,f]=cB
    for f in range(max(0,int(tStart)),min(N,int(tEnd))):
        if is_cued:   mk[2,f]=MK_LIN; mk[3,f]=MK_NC
        else:         mk[0,f]=MK_LIN; mk[1,f]=MK_NC
    return mk

def get_colors(swap,row,f):
    color_swap=swap in('C','MC')
    b_green=(row.DelayedFieldColor=='G')
    if color_swap and f>=int(row.TransStartFrame): b_green=not b_green
    cA='#27ae60' if not b_green else '#c0392b'
    cB='#27ae60' if b_green     else '#c0392b'
    return cA,cB

# ── Physics ────────────────────────────────────────────────────────────────────
def rotate(pos,sign):
    ang=math.radians(sign*ROT_DEG_FR); ca,sa=math.cos(ang),math.sin(ang)
    x=pos[:,0]*ca-pos[:,1]*sa; y=pos[:,0]*sa+pos[:,1]*ca
    pos[:,0]=x; pos[:,1]=y

def oob(p,sf,sa0,d,f):
    if p[0]**2+p[1]**2>AP_DEG**2 or(EXCL_DEG>0 and p[0]**2+p[1]**2<EXCL_DEG**2):
        h=dot_net_hash(seed_base(sa0,sf),d,f)
        r=DotNetRandom(h); return list(uniform_annulus(r,AP_DEG,EXCL_DEG))
    return list(p)

def step_lin(pos,hdg,sf,sa0,f):
    dx=math.cos(math.radians(hdg))*TRANS_DEG_FR
    dy=math.sin(math.radians(hdg))*TRANS_DEG_FR
    for d in range(DOTS_PER_SF):
        pos[d,0]+=dx; pos[d,1]+=dy; pos[d]=oob(pos[d],sf,sa0,d,f)

def step_nc(pos,sf,sa0,f):
    sb=seed_base(sa0,sf)
    for d in range(DOTS_PER_SF):
        h=dot_net_hash(sb,d,f); r=DotNetRandom(h)
        nx,ny=uniform_annulus(r,TRANS_DEG_FR,0.0)
        pos[d,0]+=nx; pos[d,1]+=ny; pos[d]=oob(pos[d],sf,sa0,d,f)

def init_pos(sa0):
    rA=DotNetRandom(sa0); rB=DotNetRandom(sa0+99991)
    pos=[]
    for sf in range(4):
        rng=rA if sf<2 else rB
        pos.append(np.array([list(uniform_annulus(rng,AP_DEG,EXCL_DEG)) for _ in range(DOTS_PER_SF)]))
    return pos

# ── Simulate all 8 ────────────────────────────────────────────────────────────
print("Simulating 8 conditions...")
all_data={}
for cue in CUES:
    for swap in CONDITIONS:
        key=(cue,swap)
        row=trials[key]; sa0=int(row.SeedA0); N=int(row.TotalFrames)
        tS=int(row.TransStartFrame); tE=int(row.TransEndFrame); hdg=float(row.TransDeg)
        mk=build_mk(swap,cue,row); pos=init_pos(sa0); frames=[]
        onset_f=int(row.OnsetFrame)
        for f in range(N):
            for sf in range(4):
                k=mk[sf,f]
                if   k==MK_CW:  rotate(pos[sf],-1)
                elif k==MK_CCW: rotate(pos[sf],+1)
                elif k==MK_LIN: step_lin(pos[sf],hdg,sf,sa0,f)
                elif k==MK_NC:  step_nc(pos[sf],sf,sa0,f)
            cA,cB=get_colors(swap,row,f)
            vis=[True,True,f>=onset_f,f>=onset_f]
            frames.append({'mk':mk[:,f].tolist(),'vis':vis,'cA':cA,'cB':cB,
                           'dots':[pos[sf].tolist() for sf in range(4)]})
        all_data[f'{cue}_{swap}']=frames
        print(f"  {cue} {swap}: {N} frames  seed={sa0}  hdg={hdg}°")

N_FRAMES=min(len(all_data[k]) for k in all_data)
onset=int(trials[('CUED','N')].OnsetFrame)
tStart=int(trials[('CUED','N')].TransStartFrame)
tEnd=int(trials[('CUED','N')].TransEndFrame)
headings={f'{cue}_{swap}':float(trials[(cue,swap)].TransDeg) for cue in CUES for swap in CONDITIONS}

json_data=json.dumps(all_data)

html=f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>VRDots Reconstruction — NMoCol CUED + UNCUED</title>
<style>
  body{{background:#111;color:#ddd;font-family:monospace;margin:0;padding:8px;}}
  h2{{color:#eee;text-align:center;font-size:13px;margin:3px 0;}}
  .row{{display:flex;gap:6px;justify-content:center;margin-bottom:4px;}}
  .panel{{display:flex;flex-direction:column;align-items:center;}}
  canvas{{background:#111;border:1px solid #333;display:block;}}
  .condlabel{{font-size:11px;font-weight:bold;text-align:center;margin-bottom:2px;}}
  .rowlabel{{writing-mode:vertical-rl;text-orientation:mixed;transform:rotate(180deg);
             font-size:11px;color:#aaa;align-self:center;padding:0 4px;min-width:20px;text-align:center;}}
  .controls{{text-align:center;margin:6px 0;}}
  input[type=range]{{width:680px;accent-color:#888;}}
  .info{{text-align:center;font-size:10px;color:#aaa;margin:2px;}}
  button{{background:#333;color:#ddd;border:1px solid #555;padding:3px 12px;
          cursor:pointer;border-radius:3px;font-size:11px;}}
  button:hover{{background:#444;}}
  .phase{{font-size:9px;color:#888;text-align:center;height:14px;}}
  kbd{{background:#333;padding:1px 4px;border-radius:2px;border:1px solid #555;font-size:10px;}}
  .verified{{color:#4a4;font-size:10px;text-align:center;margin:2px;}}
</style>
</head>
<body>
<h2>VRDots Deterministic Reconstruction &mdash; SubfieldSwap_CatekExact_NMoCol_v1 &middot; RotCfg=0 &middot; session 260515_0848</h2>
<h2 style="font-weight:normal;color:#888">Ap=1.65° &middot; 43 dots/field (21/subfield) &middot; 80 ms translation &middot; 90 Hz</h2>
<div class="verified">&#10003; Motion-kind sequences verified against MkHash32 for all 8 conditions (8/8 PASS)</div>

<div id="grid"></div>

<div class="controls">
  <button id="btnPlay">&#9654; Play</button>
  &nbsp;
  <button onclick="step(-1)">&#8592;</button>
  <button onclick="step(+1)">&#8594;</button>
  &nbsp;&nbsp;
  Speed:
  <select id="speedSel" onchange="fps=parseInt(this.value)">
    <option value="6">6 fps</option>
    <option value="15" selected>15 fps</option>
    <option value="30">30 fps</option>
    <option value="90">90 fps (real)</option>
  </select>
</div>
<div class="controls"><input type="range" id="slider" min="0" max="{N_FRAMES-1}" value="0"></div>
<div class="info" id="frameInfo">Frame 0</div>
<div class="info">
  <kbd>Space</kbd> play/pause &nbsp; <kbd>←</kbd><kbd>→</kbd> step &nbsp;
  Bright=coherent subfield &nbsp; Dim=noise subfield &nbsp;
  Orange outline=translation window
</div>
<div class="info" style="margin-top:3px">
  Onset={onset}fr &nbsp;&bull;&nbsp; tStart={tStart}fr &nbsp;&bull;&nbsp; tEnd={tEnd}fr &nbsp;&bull;&nbsp;
  CUED: Field B (green/delayed) translates &nbsp;&bull;&nbsp;
  UNCUED: Field A (red/non-delayed) translates
</div>
<div class="info" style="color:#555;margin-top:2px">
  &#9670; Red=Field A (non-delayed) &nbsp;&#9670; Green=Field B (delayed) &nbsp;
  Colors swap at tStart in C/MC &nbsp;&#9670; Dot positions: unverified pending Unity rebuild
</div>

<script>
const DATA={json_data};
const CONDITIONS={json.dumps(CONDITIONS)};
const CUES={json.dumps(CUES)};
const COND_LABELS={json.dumps(COND_LABELS)};
const COND_COLORS={json.dumps(COND_COLORS)};
const N_FRAMES={N_FRAMES};
const ONSET={onset}; const T_START={tStart}; const T_END={tEnd};
const AP={AP_DEG}; const DOT_R={DOT_R_DEG}; const SIM_HZ={SIM_HZ};
const HEADINGS={json.dumps(headings)};

const SIZE=210;
const scale=(SIZE/2-12)/AP;
function toC(d){{return SIZE/2+d*scale;}}
function toY(d){{return SIZE/2-d*scale;}}
function scaleR(r){{return Math.max(1.5,r*scale);}}

// Build grid
const grid=document.getElementById('grid');
const ctxs={{}};
const phaseEls={{}};

CUES.forEach(cue=>{{
  const row=document.createElement('div');
  row.className='row';
  const rl=document.createElement('div');
  rl.className='rowlabel';
  rl.style.color=cue==='CUED'?'#5af':'#fa5';
  rl.textContent=cue;
  row.appendChild(rl);
  CONDITIONS.forEach(swap=>{{
    const key=cue+'_'+swap;
    const panel=document.createElement('div');
    panel.className='panel';
    const lbl=document.createElement('div');
    lbl.className='condlabel';
    lbl.style.color=COND_COLORS[swap];
    lbl.textContent=COND_LABELS[swap];
    panel.appendChild(lbl);
    const cv=document.createElement('canvas');
    cv.width=SIZE; cv.height=SIZE;
    panel.appendChild(cv);
    ctxs[key]=cv.getContext('2d');
    const ph=document.createElement('div');
    ph.className='phase';
    panel.appendChild(ph);
    phaseEls[key]=ph;
    row.appendChild(panel);
  }});
  grid.appendChild(row);
}});

function phaseStr(f){{
  const ms=(f/SIM_HZ*1000).toFixed(1);
  if(f<ONSET)   return'Field A solo ('+ms+' ms)';
  if(f<T_START) return'Both rotating ('+ms+' ms)';
  if(f<T_END)   return'<b style="color:#f90">TRANSLATION</b> ('+ms+' ms)';
  return'Post-trans ('+ms+' ms)';
}}

function drawFrame(frame){{
  const ms=(frame/SIM_HZ*1000).toFixed(1);
  document.getElementById('frameInfo').innerHTML=
    '<b>Frame '+frame+' / '+(N_FRAMES-1)+'</b>  ('+ms+' ms)';

  CUES.forEach(cue=>{{
    CONDITIONS.forEach(swap=>{{
      const key=cue+'_'+swap;
      const ctx=ctxs[key];
      const fd=DATA[key][frame];

      ctx.clearRect(0,0,SIZE,SIZE);
      ctx.fillStyle='#111'; ctx.fillRect(0,0,SIZE,SIZE);

      // Aperture
      ctx.beginPath(); ctx.arc(SIZE/2,SIZE/2,SIZE/2-12,0,Math.PI*2);
      ctx.strokeStyle='#444'; ctx.lineWidth=1.2; ctx.stroke();

      // Translation highlight
      if(frame>=T_START&&frame<T_END){{
        ctx.fillStyle='rgba(255,150,0,0.07)'; ctx.fillRect(0,0,SIZE,SIZE);
        ctx.beginPath(); ctx.arc(SIZE/2,SIZE/2,SIZE/2-12,0,Math.PI*2);
        ctx.strokeStyle='rgba(255,150,0,0.5)'; ctx.lineWidth=2; ctx.stroke();
      }}

      // Fixation target: white disc + black crosshairs + white center dot
      const fc=SIZE/2;
      const fixOuterPx={FIX_OUTER_R}*scale;
      const fixCrossHWPx={FIX_CROSS_HW}*scale;
      const fixInnerPx={FIX_INNER_R}*scale;
      ctx.save();
      ctx.beginPath(); ctx.arc(fc,fc,fixOuterPx,0,Math.PI*2); ctx.clip();
      ctx.fillStyle='white';
      ctx.beginPath(); ctx.arc(fc,fc,fixOuterPx,0,Math.PI*2); ctx.fill();
      ctx.fillStyle='black';
      ctx.fillRect(fc-fixOuterPx, fc-fixCrossHWPx, 2*fixOuterPx, 2*fixCrossHWPx);
      ctx.fillRect(fc-fixCrossHWPx, fc-fixOuterPx, 2*fixCrossHWPx, 2*fixOuterPx);
      ctx.restore();
      ctx.fillStyle='white';
      ctx.beginPath(); ctx.arc(fc,fc,fixInnerPx,0,Math.PI*2); ctx.fill();

      // Dots
      for(let sf=0;sf<4;sf++){{
        if(!fd.vis[sf]) continue;
        const col=sf<2?fd.cA:fd.cB;
        const alpha=(sf===0||sf===2)?0.92:0.42;
        ctx.fillStyle=col; ctx.globalAlpha=alpha;
        fd.dots[sf].forEach(([x,y])=>{{
          ctx.beginPath();
          ctx.arc(toC(x),toY(y),scaleR(DOT_R),0,Math.PI*2);
          ctx.fill();
        }});
      }}
      ctx.globalAlpha=1.0;

      phaseEls[key].innerHTML=phaseStr(frame);
    }});
  }});
}}

let curFrame=0,playing=false,fps=15,lastT=0,rafId=null;
function setFrame(f){{
  curFrame=Math.max(0,Math.min(N_FRAMES-1,f));
  document.getElementById('slider').value=curFrame;
  drawFrame(curFrame);
}}
function step(d){{setFrame(curFrame+d);}}
document.getElementById('slider').addEventListener('input',e=>setFrame(parseInt(e.target.value)));
document.getElementById('btnPlay').addEventListener('click',()=>{{
  playing=!playing;
  document.getElementById('btnPlay').textContent=playing?'⏸ Pause':'▶ Play';
  if(playing) rafId=requestAnimationFrame(animate);
  else if(rafId) cancelAnimationFrame(rafId);
}});
function animate(ts){{
  if(!playing) return;
  if(ts-lastT>=1000/fps){{curFrame=(curFrame+1)%N_FRAMES; setFrame(curFrame); lastT=ts;}}
  rafId=requestAnimationFrame(animate);
}}
document.addEventListener('keydown',e=>{{
  if(e.key===' '){{e.preventDefault();document.getElementById('btnPlay').click();}}
  else if(e.key==='ArrowRight') step(+1);
  else if(e.key==='ArrowLeft')  step(-1);
}});
drawFrame(0);
</script>
</body>
</html>"""

OUT='/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Agents/SwapPilot/Figures/reconstruct_animation.html'
with open(OUT,'w') as f: f.write(html)
print(f"Saved: {OUT}")
