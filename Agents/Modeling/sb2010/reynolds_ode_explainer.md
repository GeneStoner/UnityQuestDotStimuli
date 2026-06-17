# The differential equation in Reynolds et al. (1999), in plain language

*An internal explainer. Audience: a sharp person who took calculus a long
time ago and would like the intuition back, not the machinery.*

The whole biased-competition model rests on one little differential
equation (their Eq. 3):

```
dy/dt = (B − y)·E  −  y·I  −  A·y
```

Everything else in the model — including the formula we actually use,
`R_TD = K·E/(E + I + σ)` — is just this equation's resting point. So it is
worth understanding what it says.

---

## 1. What `dy/dt` means (the 45-year refresher)

`y` is the firing rate of the neuron we care about — how fast it is sending
out spikes right now. It changes over time.

`dy/dt` is just **"the rate at which y is changing"** — its speed, like the
speedometer for `y`. If `dy/dt` is positive, the firing rate is climbing; if
negative, it's falling; if zero, it's holding steady. That's all the
calculus you need here. The equation is a *rule that tells the firing rate
how fast to go up or down, given what's being fed into the neuron at this
instant.*

Think of it like the water level in a sink. `y` is the level. `dy/dt` is
whether the level is rising or falling. The faucet adds water; the drain
removes it. The equation is the bookkeeping of faucet-minus-drain.

---

## 2. The three terms = three forces on the firing rate

The right-hand side has three pieces that are added up. Each pushes `y` up
or down.

**`(B − y)·E` — excitation (the faucet).**
`E` is the total **excitatory** input (in our model, the translation
signal). This term is positive, so it pushes the firing rate **up**. Two
nice features:
- It's proportional to `E`: more excitatory input → faster rise.
- It's proportional to `(B − y)`: `B` is the neuron's **maximum possible**
  firing rate, and `(B − y)` is "how much headroom is left." When the cell
  is far below its ceiling, excitation drives it hard; as `y` approaches
  `B`, the term shrinks to zero. So the cell **can never exceed `B`** — the
  response saturates gracefully. (This "multiply by the remaining room"
  trick is called *shunting*.)

**`− y·I` — inhibition (one of the drains).**
`I` is the total **inhibitory** input (in our model, the summed rotation
signals — the competitors). The minus sign pushes `y` **down**. Note it's
proportional to `y` itself: the more active the cell already is, the more
this inhibition takes away. That's the key to **divisive** (as opposed to
simply subtractive) inhibition — inhibition acts like a *percentage tax* on
the current rate, not a flat fee.

**`− A·y` — passive leak (the always-open drain).**
Even with no inhibition, a neuron's activity decays back toward zero on its
own. `A` is the leak rate; `− A·y` drains the cell in proportion to how
active it is. This is what makes the resting state `y = 0` when nothing is
driving the cell.

So: **faucet `(B−y)E` up, two drains `yI` and `Ay` down.** The firing rate
rises or falls until the faucet exactly balances the drains.

---

## 3. Where it settles: the steady state (their Eq. 4)

In an experiment the inputs `E` and `I` are roughly steady for a while, so
the firing rate stops changing and **settles** at an equilibrium. "Settled"
means the speedometer reads zero: `dy/dt = 0`. Set the right-hand side to
zero and solve for `y`:

```
(B − y)E − yI − Ay = 0
B·E − y·E − y·I − A·y = 0
B·E = y·(E + I + A)
y  =  B·E / (E + I + A)
```

That last line is **Eq. 4** — the resting firing rate. It's plain algebra
once you accept that "settled" means `dy/dt = 0`. Our translation detector
*is* this formula, with cosmetic renaming: `B → K`, `A → σ`, and the
inputs being the translation drive (`E`) and the summed rotations (`I`):

```
R_TD = K·E / (E + I + σ)
```

---

## 4. Why this particular form matters

**It's divisive normalization.** Look at the steady state: the excitatory
drive `E` sits in the numerator, but the denominator is `E + I + A`. The
response is the excitation **divided by** a pool that grows with both the
excitation and the inhibition. The output is therefore a *ratio*, not a raw
sum. This single idea explains a remarkable amount of cortex:
- **Saturation / gain control:** doubling all inputs barely changes the
  ratio, so neurons stay sensitive across a huge range of input strengths.
- **Competition:** adding a competing stimulus loads the denominator
  (`I` goes up) and *suppresses* the response — exactly what Reynolds et al.
  measured when a second stimulus entered a V2/V4 receptive field, and what
  Recanzone (1997) and Treue & Maunsell (1996) found in motion areas MT/MST.

**Why we usually use the steady state and not the full ODE.** The ODE
describes *how* the firing rate slides into its equilibrium and how fast
(the approach has a time constant of about `1/(E + I + A)` — bigger total
input means a quicker settle). For most of our purposes the neural dynamics
are fast relative to the stimulus, so the cell is essentially always "at
rest" for the current inputs, and the algebraic Eq. 4 is all we need. When
we *do* care about the shape of the transient response in time (e.g. the
rise-and-fall of `R_TD` during the brief 40-ms translation), we let the
inputs themselves carry the dynamics — the rotation and translation signals
are passed through adapting channels first, and the detector reads out their
instantaneous ratio.

**Relevance to our experiments.** The competitors in the denominator are
the two rotating dot fields. The cued/uncued advantage is, in this
framework, nothing more than a difference in `I`: when the cued field
translates, the surviving rotation in the normalization pool is the
older, more-adapted (weaker) one, so `I` is smaller and `R_TD` is larger —
better detection. The motion-competition story is this equation plus an
account of *why the two rotation inputs are unequal* (adaptation, in
Stoner & Blanc; attention, in Reynolds & Heeger).

---

## 5. One-paragraph version

`dy/dt = (B−y)E − yI − Ay` is a balance sheet for a neuron's firing rate:
excitation pushes it up but only into the room left below a ceiling `B`,
inhibition and leak pull it down in proportion to how active it already is.
Left alone with steady inputs it coasts to the point where push equals pull,
which works out by simple algebra to `y = BE/(E+I+A)` — excitation divided
by excitation-plus-inhibition-plus-a-constant. That ratio is *divisive
normalization*, the cortex's way of staying sensitive while letting stimuli
compete, and it is exactly the rule our translation detector obeys.
