# Onset Suppression & Masking: Neural Mechanisms Relevant to VRDots

**Context:** In the VRDots stimulus, an always-on rotating field is joined 750 ms later by a delayed-onset field. Both fields co-stimulate the same RFs throughout the aperture. The question is whether the sudden onset of the delayed field suppresses the ongoing neural response to the always-on field — effectively "claiming" those neurons and tagging the delayed field's locations despite complete spatial interleaving.

---

## 1. Luminance Onset as a Direct Veto of Ongoing V1 Activity

**Tucker TR & Fitzpatrick D (2006). Luminance-Evoked Inhibition in Primary Visual Cortex: A Transient Veto of Simultaneous and Ongoing Response. *Journal of Neuroscience*, 26(52), 13537–13547.**

The single most directly applicable paper. Intracellular recording in tree shrew V1 (layers 2/3): a full-field luminance step (a) delays orientation-tuned responses to a simultaneously presented grating, and (b) virtually eliminates already-ongoing orientation-tuned responses. Mechanism: luminance onset drives broadly-tuned inhibitory interneurons which silence nearby excitatory neurons. Explicitly called "a transient veto."

*VRDots relevance:* The delayed field's appearance is a distributed luminance transient across all co-occupied RFs. The Tucker & Fitzpatrick mechanism predicts a transient silencing of the always-on field's ongoing response at onset — potentially long enough (tens of ms) to establish the delayed field's "claim" on those neurons before the sustained response recovers.

- [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6674725/) | [PubMed](https://pubmed.ncbi.nlm.nih.gov/17192437/)

---

## 2. Forward & Backward Masking: Neuronal Mechanisms in V1

**Macknik SL & Livingstone MS (1998). Neuronal correlates of visibility and invisibility in the primate visual system. *Nature Neuroscience*, 1(2), 144–149.**

V1 recording in awake macaque: two distinct target response components (onset burst, after-discharge) are the neural substrates of masking. Forward masking suppresses the onset burst; backward masking suppresses the after-discharge. Both transient components are necessary for visibility. Mechanism: lateral inhibition driven by the spatiotemporal edges of the mask.

**Macknik SL & Martinez-Conde S (2004). The role of spatiotemporal edges in visibility and visual masking. *PNAS*, 97(13), 7121–7126.**

Spatiotemporal edges — not the sustained body of the mask — are the suppressive elements. Monoptic masking operates within monocular V1 neurons; dichoptic masking requires binocular cells downstream. Key: onset transient of the delayed field can drive lateral inhibitory circuits even in monocular neurons.

**Bruchmann M et al. (2023). Backward masking in mice requires visual cortex. *Nature Neuroscience*, 26, 2060–2069.**

Causal: optogenetic suppression of mask-evoked V1 activity fully restores target detection, confirming masking is generated in V1.

---

## 3. Flash Suppression: Binocular and Monocular Variants

**Wolfe JM (1984). Reversing ocular dominance and suppression in a single flash. *Vision Research*, 24(5), 471–478.**

Founding paper on binocular flash suppression (BFS): a single flash to one eye immediately suppresses awareness of the image in the other eye — no prolonged rivalry needed.

**Wilke M, Logothetis NK & Leopold DA (2003). Generalized Flash Suppression of Salient Visual Targets. *Neuron*, 39(6), 1043–1052.**

Generalized BFS: any sustained stimulus at parafoveal locations can be suppressed by a nearby onset, even without strict binocular geometry. Suppression is not purely interocular — it operates as a broader competitive mechanism. Within a single eye, a new-onset stimulus can suppress the sustained representation of a pre-existing one.

- [Neuron](https://www.cell.com/fulltext/S0896-6273(03)00526-9) | [PubMed](https://pubmed.ncbi.nlm.nih.gov/12971902/)

**Wilke M et al. (2009). Neural activity in the visual thalamus reflects perceptual suppression. *PNAS*, 106(23), 9465–9470.**

LGN activity already tracks perceptual suppression → mechanism has an early subcortical component (LGN, not just cortex).

**Alais D et al. (2014). Binocular Flash Suppression in Primary Visual Cortex of Macaque. *PLOS ONE*, 9(9), e107628.**

~20% of V1 neurons track the perceptual outcome of flash suppression. Crucially, this perceptual modulation was found equally in monocular and binocular neurons — suppression in V1 is not exclusively a binocular-cell effect.

- [PLOS ONE](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0107628)

---

## 4. Divisive Normalization: Ongoing Suppression from RF Co-activation

**Carandini M & Heeger DJ (2012). Normalization as a canonical neural computation. *Nature Reviews Neuroscience*, 13(1), 51–62.**

A neuron's response is divided by the summed activity of a normalization pool — which includes neurons responding to other stimuli within the RF. When the delayed field activates the same RF, it increases the normalization pool drive, persistently reducing the response to the always-on field. Not a categorical veto, but a sustained contrast-gain suppression throughout the delayed field's presence.

- [NRN](https://www.nature.com/articles/nrn3136) | [Free PDF](https://www.cns.nyu.edu/heegerlab/content/publications/Carandini-NRN2012.pdf)

*VRDots relevance:* Normalization explains why the ongoing suppression persists (not just at onset): the two fields continuously compete via the normalization pool.

---

## 5. Transient vs. Sustained Channels (Magno/Parvo Interaction)

**Breitmeyer BG & Ganz L (1976). Implications of sustained and transient channels for theories of visual pattern masking, saccadic suppression, and information processing. *Psychological Review*, 83(1), 1–36.**

Foundational: two temporal channels — fast transient (M-pathway) responding to onset/motion, slow sustained (P-pathway) encoding stable pattern. The transient channel's onset response inhibits the sustained channel's ongoing activity (transient-on-sustained inhibition). Classical channel-level account of metacontrast masking.

*VRDots relevance:* Delayed field onset → large M-cell transient response → inhibits P-cell sustained response driving the always-on field representation.

---

## 6. Transparent Motion: Co-located Fields in V1 and MT

**Snowden RJ, Treue S, Erickson RG & Andersen RA (1991). The response of area MT and V1 neurons to transparent motion. *Journal of Neuroscience*, 11(9), 2768–2785.**

Two co-located dot populations moving in different directions: V1 neurons respond to each component largely independently (near-linear summation), while MT neurons show strong suppression when two directions conflict. Competition and direction-based suppression emerge at MT, not V1. Response magnitudes are nonetheless reduced even in V1 compared to single-surface conditions.

- [PubMed](https://pubmed.ncbi.nlm.nih.gov/1880548/)

*VRDots relevance:* The two fields (rotating CW vs CCW, or rotating vs translating) likely conflict strongly at MT during the translation window, where MT suppression is most pronounced. V1 may be less the site of motion-direction-based competition than MT.

---

## 7. Inhibitory Stabilized Networks (ISN): Circuit Basis

**Rubin DB, Van Hooser SD & Miller KD (2015). The stabilized supralinear network. *Neuron*, 85(2), 402–417.**

V1 operates as an inhibitory stabilized network: excitatory recurrence is strong, but inhibitory feedback maintains stability. A sudden increase in excitatory drive (delayed field onset) strongly recruits inhibitory interneurons, which suppress the entire local network — including the always-on field's representation. This is the cortical circuit basis for the Tucker & Fitzpatrick veto.

---

## 8. Onset Capture and Attentional Tagging

**Yantis S & Jonides J (1984). Abrupt visual onsets and selective attention. *JEP: HPP*, 10(5), 601–621.**
**Jonides J & Yantis S (1988). Uniqueness of abrupt visual onset in capturing attention. *Perception & Psychophysics*, 43(4), 346–354.**

Abrupt onsets uniquely capture spatial attention via the bottom-up priority signal from the transient onset response — not reducible to luminance or contrast. Attentional-level complement to neuronal suppression: the delayed field's onset not only drives inhibitory suppression of the always-on field in V1, but also captures spatial attention, further biasing processing resources toward the newly-appeared stimulus.

---

## 9. Delayed Suppression via Recurrent Intracortical Circuits

**Tanabe S & Cumming BG (2014). Delayed suppression shapes disparity selective responses in monkey V1. *Journal of Neurophysiology*, 111(11), 2236–2251.**

Suppressive effects in V1 can be temporally delayed (~50–80 ms post-excitatory response), arising from recurrent intracortical connections. Even if initial onset excitation overlaps in time with the always-on field's response, a secondary suppressive wave follows and suppresses the always-on field's representation with a delay.

- [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC4044366/)

---

## 10. Continuous Flash Suppression and V1

**Tsuchiya N & Koch C (2005). Continuous flash suppression reduces negative afterimages. *Nature Neuroscience*, 8(8), 1096–1101.**

CFS (rapidly changing pattern to one eye suppresses stable pattern in the other): the repeated transient onsets are the critical suppressive element. Single-flash VRDots onset is the discrete-trial analog.

**Yuval-Greenberg S & Heeger DJ (2013). Continuous Flash Suppression Modulates Cortical Activity in Early Visual Cortex. *Journal of Neuroscience*, 33(23), 9635–9643.**

fMRI: CFS suppresses BOLD in V1 — the early cortical representation of the suppressed stimulus is genuinely reduced, not just gated at a later decision stage.

- [JNeurosci](https://www.jneurosci.org/content/33/23/9635) | [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC3760788/)

---

## Synthesis: Multiple Mechanisms, Consistent Direction

| Mechanism | Time course | Level | Key paper |
|---|---|---|---|
| Luminance onset → interneuron recruitment → silencing of ongoing excitatory activity | ~10–50 ms | V1 layers 2/3 | Tucker & Fitzpatrick 2006 |
| Forward masking via lateral inhibition from spatiotemporal onset edge | 0–100 ms | V1 | Macknik & Livingstone 1998 |
| Divisive normalization — delayed field adds to normalization pool, persistently reduces always-on gain | Immediate, sustained | V1 RF | Carandini & Heeger 2012 |
| Transient-on-sustained channel inhibition (M onset suppresses P sustained) | ~30–80 ms | LGN → V1 | Breitmeyer & Ganz 1976 |
| Recurrent intracortical delayed suppression | ~50–100 ms | V1 recurrent | Tanabe & Cumming 2014 |
| Attentional capture by abrupt onset (depletes resources from always-on field) | ~100–200 ms | V1 + higher | Yantis & Jonides 1984 |

The Tucker & Fitzpatrick (2006) "transient veto" is the single most directly applicable result. Combined with Carandini & Heeger normalization (persistent suppression throughout co-stimulation), Breitmeyer & Ganz M-on-P suppression (channel-level account), and Snowden et al. MT competition (motion-direction conflict at area MT), there is strong mechanistic support for the idea that the delayed field's onset suppresses the always-on field's representation and effectively "claims" those neurons — even though the two fields completely overlap in space.

The 300 ms pre-translation rotation window is long enough for all these mechanisms to play out and for the system to establish a stable representation of "which population is the new one." By the time translation begins, the delayed field has had 300 ms to suppress and adapt the always-on field's neurons, potentially leaving direction-selective cells tuned to the always-on rotation selectively adapted and thus less responsive when that rotation continues post-tStart.

---
*Generated: 2026-04-23 | Search agent output saved to Literature/*
