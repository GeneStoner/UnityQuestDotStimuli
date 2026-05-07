# Motion Competition Dynamics: Temporal Literature

**Context:** How quickly does direction-selective competition/suppression establish itself in MT, and what does this mean for interpreting the Stoner & Blanc (2010) motion-swap null result?

**Core question:** Is the motion swap at tStart too late to reverse a competitive state already consolidated during the 300 ms pre-translation rotation?

---

## Key Numbers

| Paper | Finding | Timescale |
|---|---|---|
| Krekelberg et al. 2011 *PNAS* | **25 ms exposure sufficient for measurable direction-selective adaptation** | 25 ms |
| Lisberger & Movshon 1999 *J Neurosci* | Transient-to-sustained adaptation in MT | 20–80 ms |
| Kohn & Movshon 2003 *Neuron* | Contrast gain reduction from adaptation | 20–80 ms |
| Osborne, Bialek & Lisberger 2004 *J Neurosci* | MT direction info 80% saturated | ~100 ms |
| Smith, Majaj & Movshon 2005 *Nat Neurosci* | Pattern-selective (PDS) neurons reach full selectivity 50–75 ms after CDS neurons | 50–75 ms lag |
| Priebe, Churchland & Lisberger 2002 *J Neurophysiol* | **Recovery from adaptation takes 125–250 ms** | 125–250 ms |
| Burr & Santoro 2001 *Vision Res* | Local motion integration saturates at ~200–300 ms | 200–300 ms |
| Okazawa et al. 2018 *eNeuro* | Recency bias in psychophysical temporal integration kernels | ~100–500 ms |

**Critical arithmetic:** The 300 ms pre-translation rotation is 4–15 adaptation time constants deep (at 20–80 ms/time constant). Recovery requires 125–250 ms. The translation window is only 80 ms. The swap cannot reset the competitive state before translation ends.

---

## 1. MT Motion Opponency with Transparent Stimuli

**Snowden RJ, Treue S, Erickson RG & Andersen RA (1991). The response of area MT and V1 neurons to transparent motion. *Journal of Neuroscience*, 11(9), 2768–2785.**
- MT neurons tuned to one direction are suppressed by a superimposed dot field moving in the opposite direction
- V1 neurons were NOT suppressed — the competition emerges at MT, not V1
- Counter-rotating dot fields (the VRDots stimulus class) produce this opponent suppression throughout the pre-translation period
- [PubMed](https://pubmed.ncbi.nlm.nih.gov/1880548/)

**Heeger DJ et al. (1999). Motion Opponency in Visual Cortex. *Journal of Neuroscience*, 19(16), 7162–7174.**
- Confirmed motion opponency in human MT+ (fMRI); absent in V1
- Response to two counter-rotating fields < sum of individual responses
- [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6782843/) | [PDF](https://www.cns.nyu.edu/heegerlab/content/publications/Heeger-jneurosci99.pdf)

**Qian N, Andersen RA & Adelson EH (1994). Transparent motion perception as detection of unbalanced motion signals. *Journal of Neuroscience*, 14(12), parts I–III.**
- Transparent motion requires locally unbalanced motion signals; opponent suppression in MT is the mechanism
- Counter-rotating fields are at the edge of transparent perception — the system is continuously engaged in resolving opponent signals
- [PubMed Part I](https://pubmed.ncbi.nlm.nih.gov/7996181/) | [PDF Part I](https://persci.mit.edu/pub_pdfs/qian94_1.pdf)

---

## 2. Short-Term Adaptation in MT: Time Course

**Lisberger SG & Movshon JA (1999). Visual motion analysis for pursuit eye movements in area MT. *Journal of Neuroscience*, 19(6), 2224–2246.**
- MT neurons show a transient-to-sustained transition with time constants of 20–80 ms
- This short-term adaptation correlates with direction-selective suppression during sustained motion
- [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6782544/)

**Priebe NJ, Churchland MM & Lisberger SG (2002). Constraints on the Source of Short-Term Motion Adaptation in Macaque Area MT. Parts I & II. *Journal of Neurophysiology*, 88(1), 354–382.**
- Conditioning motion suppresses same-direction test responses
- **Recovery time constant: 125–250 ms** — longer than the entire 80 ms translation window
- Adaptation arises from intrinsic MT mechanisms and synaptic depression in MT inputs
- [PMC Part I](https://pmc.ncbi.nlm.nih.gov/articles/PMC2581621/) | [PMC Part II](https://pmc.ncbi.nlm.nih.gov/articles/PMC2581620/)

**Kohn A & Movshon JA (2003). Neuronal adaptation to visual motion in area MT. *Neuron*, 39(4), 681–691.**
- Adaptation operates via contrast gain reduction (not direction shift)
- Spatially specific within RF
- Transient-to-sustained transition over 20–80 ms
- [Cell.com](https://www.cell.com/neuron/fulltext/S0896-6273(03)00438-0)

**Krekelberg B, van Wezel RJA & Albright TD (2011). Perceptual and neural consequences of rapid motion adaptation. *PNAS*, 108(45), E1080–E1088.**
- **25 ms of motion exposure is sufficient for measurable direction-selective adaptation and motion aftereffect**
- Direction reversal of selectivity begins ~80 ms after test stimulus onset in adapted system
- [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC3215073/) | [PNAS](https://www.pnas.org/content/108/45/E1080)

---

## 3. Information Saturation and Pattern Motion Lag

**Osborne LC, Bialek W & Lisberger SG (2004). Time course of information about motion direction in visual area MT. *Journal of Neuroscience*, 24(13), 3210–3222.**
- Shannon information about motion direction in MT reaches **80% of maximum within the first 100 ms**
- Information saturates early; the last 200 ms of the 300 ms pre-translation period adds relatively little new competitive information
- The last ~100–150 ms before tStart is the peak-weighted epoch
- [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC2553809/) | [PDF](https://swh.princeton.edu/~wbialek/our_papers/osborne+al_04.pdf)

**Smith MA, Majaj NJ & Movshon JA (2005). Dynamics of motion signaling by neurons in macaque area MT. *Nature Neuroscience*, 8(2), 220–228.**
- CDS (component-selective) neurons respond 6 ms earlier than PDS (pattern-selective) neurons
- Pattern selectivity (encoding the rotating surface as such) takes an additional 50–75 ms to fully emerge
- Three response phases: direction-independent transient (0–80 ms) → direction-selective (80–140 ms) → sustained
- [PubMed](https://pubmed.ncbi.nlm.nih.gov/15657600/) | [PDF](https://www.cns.nyu.edu/~tony/Publications/smith-majaj-movshon-2005.pdf)

---

## 4. Temporal Weighting and Recency

**Okazawa G et al. (2018). Strategic and dynamic temporal weighting for perceptual decisions in humans and macaques. *eNeuro*, 5(5), ENEURO.0169-18.2018.**
- Psychophysical temporal integration kernels show recency bias (more common than primacy) in motion discrimination
- Effective integration window consistent within individuals: ~100–500 ms
- [eNeuro](https://www.eneuro.org/content/5/5/ENEURO.0169-18.2018)

**Burr DC & Santoro L (2001). Temporal integration of optic flow, measured by contrast and coherence thresholds. *Vision Research*, 41(15), 1891–1899.**
- Local motion integration saturates at ~200–300 ms
- 300 ms pre-translation rotation falls at the upper limit of the fast local-integration time constant
- [PubMed](https://pubmed.ncbi.nlm.nih.gov/11412882/)

---

## Synthesis: Why the S&B Motion Swap is Uninformative About Competition Mechanism

The 300 ms pre-translation rotation is 4–15 direction-selective adaptation time constants (20–80 ms each). By tStart:
1. Adaptation is maximally consolidated in the MT direction-selective population
2. Direction information in MT saturated at ~100 ms into rotation
3. Pattern-selective responses fully established after ~150–200 ms

The motion swap at tStart:
- Reverses the nominal direction labels of the two fields
- Introduces a new transient, but into neurons that require 125–250 ms to recover from their adapted state
- Cannot reverse the competitive state within the 80 ms translation window

**Conclusion:** S&B's motion-swap null result does not distinguish between adaptation-based and onset-based mechanisms. A swap timing experiment (swap at tStart−100ms, tStart−50ms, tStart, tStart+40ms) would measure the actual time constant of competition and determine when exactly the competitive outcome is sealed.

---

## Open Gaps

1. Direct millisecond-by-millisecond measurement of suppression buildup between simultaneously presented counter-rotating dot fields — not yet measured at single-unit resolution
2. Interaction between onset-triggered transient suppression and direction-selective adaptation under continuous competition — the mechanistic heart of the VRDots question
3. Recovery time constant under *continuous* opponent competition (Priebe et al. measured recovery in the absence of the adaptor)

---

*Generated: 2026-04-24 | Companion: `onset_suppression_lit.md`, `onset_competition_mechanism.md`*
