#!/usr/bin/env python3
"""ps_frontend_figure.py -- THE FRONT END, on ONE of Figure 8's V1 receptive fields.

⭐ GS 2026-08-28: "this figure should probably go after fig 8 ... we should just maybe choose one
of the V1 RFs there to illustrate the front end. so maybe just one dot, one motion to make it
clear? ... we dont want to show the trajectory though i think since we are just capturing a moment
in time."

WHAT THIS IS. `hcps_v1drive` drawn for a single receptive field at a single frame: one dot, one
Gaussian weight, two tuned weights, two raw drives, and the input normalization that follows them.
It replaces the earlier `SurfaceSelectionModel/fig_frontend_schematic.py`, which drew a stimulus
and a receptive field of its own.

⭐ WHY IT LIVES HERE AND IMPORTS `ps_stimulus_common`. Figure 2 and Figure 8 already share that
module so that their stimulus panels are THE SAME PICTURE. A front-end figure that redrew the
annulus and invented its own receptive field would put a third, subtly different stimulus on the
page. So this borrows Figure 8's RIGHT-HAND receptive field and its green dot outright.

⛔ NO TRAJECTORY. Figure 8 shows the dot's 100 + 100 ms path because dwell at V1 is 211-316 ms and
the window is 95% of one. The drive, though, is computed FRAME BY FRAME, so this figure is one
instant and shows the INSTANTANEOUS DIRECTION only -- the same convention Figure 2 uses for the MT
receptive field. Drawing a path here would imply the front end integrates over one, and it does
not.

⭐ ONE DOT IS THE TYPICAL CASE, NOT A SIMPLIFICATION. Figure 8's own caption says these receptive
fields are "small enough that a single one often contains dots of only one surface", and measured
on the sb preset (5.218 dots/deg^2 per field, sigma 0.0796-0.1856 deg) 51% of point-sets contain
NO dot inside FWHM/2, 29% contain exactly one, and 20% two or more. One dot is the modal
non-empty receptive field.

⚠️ AND SO THE BAR GRAPHS CARRY NO HUE. The previous version stacked each bar in red and green to
show which dot contributed it -- which put a colour code inside a graph about direction, exactly
the conflation GS queried. With one dot there is nothing to stack: each bar is solid in its own
stream's ink. The two-hue point survives on the hue axis and in one caption line.

⚠️ ROTATION SENSES FOLLOW THIS MODULE, WHICH IS THE OPPOSITE OF THE OTHER SCHEMATIC FAMILY.
Here green = field B = CW = cued/delayed-onset and red = field A = CCW = uncued/first-on. In
`fig_tiled_schematic` / `hcps_vrstim` green is CCW. That inconsistency is already on the record as
open; this figure does NOT resolve it, it inherits Figure 8's convention because it inherits
Figure 8's stimulus. Do not "fix" one without the other.

⚠️ RECEPTIVE-FIELD CONVENTION. Figure 8's V1 RF is a HARD DISC of radius 0.24 deg (a
literature-anchored ceiling), while `hcps_v1drive` weights dots by a GAUSSIAN. They are reconciled
by reading Figure 8's radius as FWHM/2, which gives sigma = 0.24 / 1.1774 = 0.204 deg -- just above
the tiled model's own 0.08-0.19 deg range. Stated on the figure rather than glossed.
"""
import os, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch
import ps_stimulus_common as S
from ps_stimulus_common import INK, INK2, SURFACE, RED, GREEN, RF_R_DEG, DOT_DIAM_DEG

plt.rcParams["font.family"] = "serif"; plt.rcParams["mathtext.fontset"] = "cm"
HERE = os.path.dirname(os.path.abspath(__file__))
MUTE, LINE, STIM, COOP = "#6b6560", "#9a938a", "#303036", "#0072B2"
# ⭐ THE HUE RING, and the rule that goes with it, are Figure 11's (`fig_2ps_schematic.py`):
# "the bars use the structural palette -- never hue -- so nothing depends on telling red from
# green", and only RED and GREEN have short names, so the other six channels get a SWATCH of
# their own hue instead of a number. Both bar columns are therefore BLACK here.
# ⚠️ COPIED, not imported -- that figure lives in the other repository. Canonical source is
# `SurfaceSelectionModel/fig_2ps_schematic.py`, which took it from the website's HCPSViewer.tsx.
# If the ring changes there, change it here.
HUE_RING = ["#cf3b2f","#dd7a22","#d9c31e","#93b62b","#2f8f5b","#93b62b","#d9c31e","#dd7a22"]

KAPPA, KAPPA_HUE, NDIR, NHUE = 2.0, 2.0, 8, 8
FFSCALE, FFFLOOR = 3.0, 1.0
SIG_DEG = RF_R_DEG / (np.sqrt(2*np.log(2)))          # FWHM/2 -> sigma
OCC0, OCC1, OCC2 = 51, 29, 20

def tune(d, k): return np.maximum(np.exp(k*np.cos(d)) - np.exp(-k), 0.0)
prefs = np.arange(NDIR)*2*np.pi/NDIR

# ---- the dot: Figure 8's right-hand RF, green, at ONE frame inside the pre-probe rotation ----
p0, DCOL, SENSE, TRANSLATES, RF_C, PDIR = S.selected("right")
pre, _during = S.dot_trajectory(p0, SENSE, TRANSLATES, PDIR)
P = pre[len(pre)//2]                                  # mid pre-probe: pure rotation, no probe
# ⚠️ `local_direction` returns a UNIT VECTOR, not an angle. Converted once, here, rather than
# assumed -- the first version fed the 2-vector straight into the tuning function.
DVEC = S.local_direction(P, SENSE)                    # unit tangent at that frame
DIRV = float(np.arctan2(DVEC[1], DVEC[0]))            # ... as an angle, which the tuning needs
OFF  = float(np.hypot(P[0]-RF_C[0], P[1]-RF_C[1]))    # distance from the RF centre, deg
WG   = float(np.exp(-OFF**2/(2*SIG_DEG**2)))
HUE_DOT = np.pi                                       # green
ffM_raw = WG*tune(prefs-DIRV, KAPPA)
ffC_raw = WG*tune(prefs-HUE_DOT, KAPPA_HUE)
ffM_nrm = FFSCALE*ffM_raw/(ffM_raw.sum()+FFFLOOR)
ffC_nrm = FFSCALE*ffC_raw/(ffC_raw.sum()+FFFLOOR)
# what the neighbouring / orthogonal channels get, as a fraction of peak. COMPUTED, because the
# earlier two-dot version quoted a single "12%" that only ever applied to the +-90 deg channels.
NB1 = tune(np.pi/4, KAPPA_HUE)/tune(0.0, KAPPA_HUE)      # +-45 deg neighbours
NB2 = tune(np.pi/2, KAPPA_HUE)/tune(0.0, KAPPA_HUE)      # +-90 deg
FLOOR_FRAC = NB2

XL, YL = 21.0, 11.2
fig = plt.figure(figsize=(XL*0.62, YL*0.62)); ax = fig.add_axes([0,0,1,1])
ax.set_xlim(0,XL); ax.set_ylim(0,YL); ax.axis("off")
def nx(x): return x/XL
def ny(y): return y/YL
def box(x,y,w,h,ec,fc="white",lw=1.3,z=2):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.02,rounding_size=0.10",
                 ec=ec,fc=fc,lw=lw,zorder=z))
def fap(a,b,c,lw=1.6):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle="-|>",mutation_scale=13,lw=lw,color=c,
                 zorder=4,shrinkA=0,shrinkB=0))
def bars(x0,y0,vals,col,scale,dy=0.26,h=0.19,ticks=False,huelab=False):
    """⭐ CHANNEL 0 AT THE TOP, and the preferred value labelled in degrees beside each bar --
    both copied from `fig_bias_profile.py`, which draws Figures 9 and 10 on the same page. Those
    put channel 0 at the top and write "%d deg" to the LEFT of each bar at fontsize 8.2 in MUTE.
    An eight-channel column that ran the other way a few figures later would be read wrong.
    ⚠️ Only the RAW drive is labelled. Repeating the ticks on the normalized column would say
    nothing new and would crowd a panel whose point is the rescaling."""
    n=len(vals)
    for k,b in enumerate(vals):
        cy = y0 + (n-1-k)*dy                       # channel 0 at the TOP
        ax.add_patch(FancyBboxPatch((x0,cy),max(b*scale,0.004),h,
                     boxstyle="round,pad=0.004",fc=col,ec="none",zorder=3))
        if ticks and not huelab:
            ax.text(x0-0.06, cy+h/2, "%d°"%round(np.degrees(prefs[k])), ha="right",
                    va="center", fontsize=7.4, color=MUTE, zorder=4)
        elif ticks:
            # ⛔ NO DEGREES ON THE HUE COLUMN: those numbers are hue-ring positions, not
            # directions, and the figure already uses degrees for MOTION. Only RED and GREEN
            # have names; the other six get a swatch of their own hue. Figure 11's convention.
            deg = round(np.degrees(prefs[k]))
            if deg in (0, 180):
                ax.text(x0-0.06, cy+h/2, "RED" if deg == 0 else "GREEN", ha="right",
                        va="center", fontsize=7.4, color=HUE_RING[k], weight="bold", zorder=4)
            else:
                sw = 0.11
                ax.add_patch(FancyBboxPatch((x0-0.06-sw, cy+h/2-sw/2), sw, sw,
                             boxstyle="square,pad=0", fc=HUE_RING[k], ec="none", zorder=4))
def clean(a):
    a.set_yticks([]); a.tick_params(labelsize=7.2)
    for sp in ("top","right","left"): a.spines[sp].set_visible(False)
def ghosted(a,kap,solid_pref,solid_col,title):
    x=np.linspace(0,2*np.pi,400)
    for pk in prefs: a.plot(np.degrees(x),tune(x-pk,kap),color=LINE,lw=0.9,alpha=0.55,zorder=1)
    a.plot(np.degrees(x),tune(x-solid_pref,kap),color=solid_col,lw=2.4,zorder=3)
    a.fill_between(np.degrees(x),tune(x-solid_pref,kap),color=solid_col,alpha=0.14,zorder=2)
    a.set_title(title,fontsize=8.4); a.set_xlim(-12,372); clean(a)

# ⭐ GS 2026-08-28 asked: "The Front End? or Pre-processing?" -- THE FRONT END, because
# "pre-processing" implies an inert filtering step, and this one contains a divisive
# normalization (`ffNorm`) that materially shapes everything downstream. It is also the project's
# own word for it throughout. The "one receptive field, one dot, one frame" qualifier moves to
# the caption, where it belongs.
ax.text(0.55,10.75,"THE FRONT END",fontsize=17,weight="bold",color=INK,va="center")
ax.text(0.55,10.30,"The common input to every model that follows — hcps_vrstim → hcps_v1drive.",
        fontsize=9.8,color=MUTE,va="center",style="italic")
ax.plot([0.55,XL-0.55],[10.06,10.06],'-',color=LINE,lw=1.0)

YM, YC, HDR = 7.25, 2.75, 9.62
BW, BH = 3.05, 3.05
X1, X2, X3, X4, X5 = 0.55, 4.70, 8.40, 12.65, 16.95

# ---------------- 1 the receptive field, magnified ----------------
ax.text(X1,HDR,"1   the receptive field",fontsize=10.5,weight="bold",color=INK)
axr = fig.add_axes([nx(X1+0.15),ny(4.30),nx(3.10),ny(3.10)]); axr.set_aspect("equal")
axr.set_xlim(-1.55,1.55); axr.set_ylim(-1.55,1.55); axr.axis("off")
gg=np.linspace(-1.55,1.55,200); GX,GY=np.meshgrid(gg,gg)
axr.imshow(np.exp(-(GX**2+GY**2)/(2*(RF_R_DEG/SIG_DEG*0.5)**2)),
           extent=[-1.55,1.55,-1.55,1.55],origin="lower",cmap="Greys",alpha=0.30,
           vmin=0,vmax=1.7,zorder=0)
axr.add_patch(Circle((0,0),1.0,facecolor=SURFACE,edgecolor=INK,lw=2.2,zorder=1,alpha=0.55))
dx,dy = (P-RF_C)/RF_R_DEG
axr.add_patch(Circle((dx,dy),DOT_DIAM_DEG/2/RF_R_DEG,facecolor=DCOL,edgecolor="none",zorder=6))
axr.annotate("",xy=(dx+0.62*np.cos(DIRV),dy+0.62*np.sin(DIRV)),
             xytext=(dx+0.10*np.cos(DIRV),dy+0.10*np.sin(DIRV)),
             arrowprops=dict(arrowstyle="-|>",color=DCOL,lw=2.2,mutation_scale=16),zorder=7)
axr.text(dx,dy-0.13,"  $W_g$ = %.2f"%WG,ha="left",va="top",fontsize=8.4,color=DCOL,weight="bold")

# ⭐ THE SPATIAL PROFILE. GS 2026-08-28: "we do need to show the spatial profile/weighting don't
# we?" -- yes: W_g is a FUNCTION of distance and drawing only its value at one dot hides that.
# ⭐ It is also self-checking. The circle is drawn at FWHM/2, so the curve MUST pass through 0.5
# exactly where the circle's edge is; if it ever does not, the disc and the weighting have drifted
# apart.
axp = fig.add_axes([nx(X1+0.62),ny(2.75),nx(2.15),ny(1.25)])
xx = np.linspace(0,1.65,300)
wg = np.exp(-(xx*RF_R_DEG)**2/(2*SIG_DEG**2))
axp.plot(xx,wg,color=INK,lw=2.0,zorder=3)
axp.fill_between(xx,wg,color=INK,alpha=0.10,zorder=2)
axp.plot([1,1],[0,0.5],':',color=MUTE,lw=1.0,zorder=2)
axp.plot([0,1],[0.5,0.5],':',color=MUTE,lw=1.0,zorder=2)
d_ = OFF/RF_R_DEG
axp.plot([d_,d_],[0,WG],'-',color=DCOL,lw=1.0,alpha=0.7,zorder=3)
axp.plot(d_,WG,'o',ms=6,color=DCOL,zorder=5)
axp.set_xlim(0,1.65); axp.set_ylim(0,1.12)
axp.set_yticks([0.5,1.0]); axp.set_yticklabels(["0.5","1"])
axp.set_xticks([0,1]); axp.set_xticklabels(["centre","edge"])
axp.tick_params(labelsize=7.2)
for sp in ("top","right"): axp.spines[sp].set_visible(False)
axp.set_title("spatial weight $W_g$",fontsize=8.4)

# ---------------- 2 the tuned weights ----------------
ax.text(X2,HDR,"2   two tuned weights",fontsize=10.5,weight="bold",color=INK)
axv=fig.add_axes([nx(X2),ny(YM-0.35),nx(2.30),ny(1.40)])
ghosted(axv,KAPPA,DIRV,STIM,"direction tuning")
axv.set_xticks([0,90,180,270,360]); axv.set_xlabel("preferred direction (deg)",fontsize=7.6)
axv.plot(np.degrees(DIRV)%360,0,'^',color=DCOL,ms=8,clip_on=False,zorder=6)

axh=fig.add_axes([nx(X2),ny(YC-0.35),nx(2.30),ny(1.40)])
ghosted(axh,KAPPA_HUE,HUE_DOT,GREEN,"hue tuning")
axh.set_xticks([0,180]); axh.set_xticklabels(["RED","GREEN"])
for lab,c in zip(axh.get_xticklabels(),[RED,GREEN]): lab.set_color(c); lab.set_weight("bold")
axh.plot(180,0,'^',color=GREEN,ms=8,clip_on=False,zorder=6)

# ---------------- 3 raw drive ----------------
ax.text(X3,HDR,"3   the raw drive",fontsize=10.5,weight="bold",color=INK)
ax.text(X3,HDR-0.34,"$ff$ = the drive to one channel",fontsize=8.2,color=MUTE,style="italic")
ax.text(X3,YM+BH/2+0.24,"MOTION",fontsize=9.8,weight="bold",color=INK)
ax.text(X3,YC+BH/2+0.24,"COLOUR",fontsize=9.8,weight="bold",color=INK)
SC = 1.75/max(ffM_raw.max(),ffC_raw.max())
for (yc_,vals,col,lab) in ((YM,ffM_raw,STIM,"M"),(YC,ffC_raw,STIM,"C")):
    box(X3,yc_-BH/2,BW,BH,col,"white",1.4)
    ax.text(X3+BW/2,yc_+BH/2-0.36,r"$ff^{%s}_{i,k}=W_g\cdot tune$"%lab,fontsize=10.5,
            color=INK,ha="center")
    bars(X3+0.66,yc_-BH/2+0.22,vals,col,SC,ticks=True,huelab=(lab=="C"))

# ---------------- 4 ffNorm ----------------
ax.text(X4,HDR,"4   ffNorm, per stream",fontsize=10.5,weight="bold",color=INK)
# ⭐ GS: "i have forgotten (and naive viewers will be mystified) exactly how the normalization
# works -- why the 3 in the numerator for example." Both constants are named for what they DO.
# ⚠️ `ffScale` = 3 is a BARE LITERAL in `hcps_op.m`'s parameter struct with no derivation on
# record, and the project's own note says `ffNorm = true` "was never argued". So the label states
# its EFFECT -- the total each hypercolumn is rescaled to -- and claims no reason for the value.
ax.text(X4,HDR-0.34,"each hypercolumn's 8 channels, divided by their own sum",
        fontsize=8.2,color=MUTE,style="italic")
SN = 2.05/max(ffM_nrm.max(),ffC_nrm.max())
for (yc_,vals,col) in ((YM,ffM_nrm,STIM),(YC,ffC_nrm,STIM)):
    box(X4,yc_-BH/2,BW,BH,col,"#fafafa",1.6)
    # ⭐ SYMBOLIC, not literal. GS 2026-08-28: "maybe have a constant set to 3? i have no memory
    # as to why it was set to 3". Naming them makes them visible AS constants -- and `ffFloor` in
    # particular is a knob, not a detail: it is what decides whether a faint input keeps its
    # magnitude or is rescaled to full strength. Values are given once, below.
    ax.text(X4+BW/2,yc_+BH/2-0.44,r"$ff \leftarrow \dfrac{ffScale \cdot ff}{\sum_k ff + ffFloor}$",
            fontsize=10.5,color=col,ha="center",va="center")
    bars(X4+0.30,yc_-BH/2+0.22,vals,col,SN)
    if yc_ == YM:
        # ⚠️ Named in the text rather than pointed at. Leader lines from here either cross the box
        # or land in the header row, which is what the first attempt did.
        ax.text(X4,yc_-BH/2-0.22,"ffScale = %g   the total the 8 channels are rescaled to"%FFSCALE,
                fontsize=7.6,color=MUTE,va="top")
        ax.text(X4,yc_-BH/2-0.56,"ffFloor = %g   how much drive a receptive field must have\n"
                "                 before it is rescaled to full strength"%FFFLOOR,
                fontsize=7.6,color=MUTE,va="top",linespacing=1.4)

# ---------------- 5 the circuit ----------------
# ⭐ GS: "lets have it feed into a generic Hypercolumn and Point-Set Models. this is the common
# front end for the models to follow." So the last box names the FAMILY, not one circuit -- the
# figure sits ahead of all of them and should not appear to belong to any one.
ax.text(X5,HDR,"5   the models",fontsize=10.5,weight="bold",color=COOP)
box(X5,4.05,2.90,2.30,COOP,"white",1.4)
ax.text(X5+1.45,5.38,"HYPERCOLUMN AND",ha="center",fontsize=10.0,weight="bold",color=COOP)
ax.text(X5+1.45,5.02,"POINT-SET MODELS",ha="center",fontsize=10.0,weight="bold",color=COOP)
for a,b,c in [((X1+3.40,5.95),(X2-0.12,YM+0.15),STIM),((X1+3.40,5.75),(X2-0.12,YC+0.55),STIM),
              ((X2+2.35,YM),(X3-0.10,YM),STIM),((X2+2.35,YC),(X3-0.10,YC),STIM),
              ((X3+BW,YM),(X4-0.10,YM),STIM),((X3+BW,YC),(X4-0.10,YC),STIM),
              ((X4+BW,YM),(X5-0.10,5.92),COOP),((X4+BW,YC),(X5-0.10,4.45),COOP)]:
    fap(a,b,c)

out=os.path.join(HERE,"ps_frontend_figure.png")
fig.savefig(out,dpi=190,facecolor="white"); print("wrote",out)
print("dot offset %.4f deg (%.0f%% of RF radius), Wg %.3f, direction %.1f deg, hue GREEN"
      %(OFF,100*OFF/RF_R_DEG,WG,np.degrees(DIRV)%360))
