# Transparent Base Rates Approach the State of the Art in Conflict Forecasting

**Evidence from a fully auditable forecasting system, five preregistered covariate
failures, and equal-weight forecast pooling**

Kara Zajac
*Independent researcher* · kara@soulstone.org
Preprint · July 2026 · v1.0

Code, data, and a continuously updating deployment are public:
https://github.com/KaraZajac/TOCSIN · https://tocsin.karazajac.io ·
dataset bundle `tocsin-dataset-26.1` (CC BY 4.0).

---

## Abstract

Machine-learning systems now define the state of the art in armed-conflict
forecasting, but their opacity makes them difficult to audit, and a recurring
finding — that naive baselines are nearly as accurate — has never been given a
systematic, adversarially honest treatment by a system *designed* to be
transparent. We present TOCSIN, a conflict-forecasting system whose every
probability is a reference-class base rate: an empirically shrunk historical
frequency, conditioned on recency structure, auditable down to the individual
class counts. Evaluated walk-forward on the same target, vantages, and
information sets as the Uppsala VIEWS system (7,680 country-months across five
historical vantages), TOCSIN attains a Brier score of 0.0461 against VIEWS's
0.0412 — within 12% of the state of the art, while beating it on 70% of
individual country-months — and naive last-year persistence (0.0433) falls
between them. We then subject the system to a preregistered tune/validate
protocol and test five families of theoretically motivated covariates: regime
type, forecast-horizon decay, youth bulges, militarized-dispute and alliance
history, and ethnic exclusion (alone and interacted). All five fail
out-of-sample, despite large descriptive associations (youth bulges quadruple
onset rates; militarized-dispute history marks a 30-fold onset class among
long-quiet country pairs). We identify three mechanisms — absorption by
recency conditioning, class fragmentation under shrinkage, and, at rare-event
base rates, a formal *metric blindness* of the Brier score, for which we give
an exact decomposition showing that even perfect conditioning cannot move
aggregate Brier by more than 0.05% at pair-grain base rates. Finally,
zero-parameter equal-weight pooling of VIEWS with persistence outperforms
every individual model (0.0399, −3.3% versus VIEWS), while adding TOCSIN to
that pool *worsens* it: the transparent system wins months but duplicates the
pool's recency information rather than diversifying it. The results sharpen a
deflationary view of conflict predictability — the practical ceiling on the
standard occurrence target sits close to what recency alone delivers, and is
most cheaply approached not by richer models but by pooling diverse ones.

**Keywords:** conflict forecasting · base rates · reference-class forecasting ·
Brier score · forecast combination · preregistration · UCDP · VIEWS

---

## 1. Introduction

Armed-conflict research has taken a decisive predictive turn. Where Ward,
Greenhill and Bakke (2010) diagnosed a field optimizing statistical
significance at the expense of predictive power, there now exist standing
forecast systems — most prominently the Uppsala Violence Early-Warning System
(VIEWS; Hegre et al. 2019) — that publish monthly machine-learning forecasts
of state-based violence for every country, and organized competitions that
score them (Hegre et al. 2022; Vesco et al. 2022). The predictive turn,
however, has produced a persistent embarrassment alongside its successes:
simple baselines — last year's violence, the country's historical rate — come
uncomfortably close to the most sophisticated ensembles (Cederman & Weidmann
2017; Chadefaux 2017). This gap between methodological ambition and marginal
accuracy gain is usually reported in passing, as a caveat. It has rarely been
made the *object* of study.

This paper does so, from an unusual direction. Rather than build a richer
model and report its increment, we build the most disciplined possible version
of the *simple* alternative — a pure reference-class base-rate engine in the
tradition of clinical-versus-statistical prediction (Meehl 1954; Dawes 1979)
and outside-view forecasting (Kahneman & Lovallo 1993) — and ask three
questions with it:

1. **How close does transparent get?** When every probability is a shrunk
   historical frequency whose class definition, member counts, and shrinkage
   weights are inspectable, how much accuracy is sacrificed relative to the
   covariate-rich state of the art, scored on the state of the art's own
   target?

2. **What do covariates actually add, out-of-sample?** The conflict literature
   proposes many structural correlates of onset — regime type (Goldstone et
   al. 2010), development (Fearon & Laitin 2003; Collier & Hoeffler 2004),
   youth bulges (Urdal 2006), ethnic exclusion (Cederman, Wimmer & Min 2010),
   and dyadic dispute history (Maoz et al. 2019). We test five covariate
   families under a preregistered tune/validate protocol designed to make
   post-hoc rationalization impossible, and report all results, including —
   especially — the failures.

3. **Where do the remaining gains live?** If single-model improvements are
   exhausted, the forecast-combination literature (Bates & Granger 1969;
   Clemen 1989; Timmermann 2006) predicts that *pooling* diverse forecasters
   should beat the best of them. We test zero-parameter equal-weight pools
   against every individual system, and use the pool's composition to
   diagnose what information each system actually contributes.

The answers, in brief: transparent gets within 12% of the state of the art
(and naive persistence within 5%); all five covariate families fail
out-of-sample despite large descriptive associations, for reasons we can
mechanically identify; and an equal-weight pool of the ML system with naive
persistence beats everything, while our own system — despite winning 70% of
individual months — *subtracts* from that pool because its information is
already inside it. Together these results locate the practical ceiling of the
standard conflict-occurrence target close to what recency structure alone
delivers, and suggest the field's cheapest remaining accuracy lies in
combination and in target design rather than in additional structure.

A secondary contribution is infrastructural. The entire system — a merged,
crosswalked, CC BY-licensed dataset spanning nine sources; the engine; the
evaluation harness; a self-resolving forecast journal; and a public,
continuously updating deployment — is open and reproducible. The
preregistration machinery (§5) is, to our knowledge, the first
covariate-adoption protocol for a conflict-forecasting system that
mechanically enforces a single consultation of held-out data and the
retirement of spent validation eras.

## 2. Related work

**Conflict forecasting systems.** The Political Instability Task Force
established that parsimonious models with regime-type interactions could
anticipate instability onsets years ahead (Goldstone et al. 2010). VIEWS
(Hegre et al. 2019, 2022) is the current reference system: a monthly-updated
ensemble over UCDP data producing, among other targets, the probability of
≥25 state-based battle deaths per country-month — the target we adopt for
head-to-head comparison. Blair and Sambanis (2020) argue theory-structured
models travel better out-of-sample; Muchlinski et al. (2016) document large
in-sample gains from random forests that Colaresi and Mahmood (2017) show
require careful out-of-sample discipline to interpret.

**The baseline embarrassment.** Cederman and Weidmann (2017) caution that
conflict's rare-event structure and the dominance of history-dependence put
low ceilings on achievable gains; Chadefaux (2017) surveys the same pattern.
Our contribution is to *instrument* this claim: we reproduce it independently
(persistence within 5% of VIEWS on 7,680 scored country-months), quantify the
covariate increment under preregistration (≈0), and give an exact scoring-rule
decomposition for why large class-rate signals can be invisible to aggregate
Brier at rare-event base rates.

**Statistical versus clinical prediction and the outside view.** The engine
is a deliberate descendant of the actuarial tradition — Meehl's (1954) review,
Dawes's (1979) improper linear models, and Kahneman and Lovallo's (1993)
reference-class forecasting. Its wager is that in a domain governed by sticky,
recurrent processes, a disciplined outside view captures most extractable
signal. The five covariate failures in §6 are, in effect, a measured defense
of that wager.

**Forecast combination.** That combinations of diverse forecasts outperform
their best member is among the most replicated findings in the forecasting
literature, from Bates and Granger (1969) through Clemen's (1989) review and
the M-competitions (Makridakis & Hibon 2000). Equal weights are notoriously
hard to beat ("the forecast combination puzzle"; Timmermann 2006). Section 7
imports this machinery into the conflict domain with a zero-parameter design
that forecloses fitting-based objections, and adds a compositional diagnostic:
which member's *removal* improves the pool.

**Scoring rules.** We score with the Brier (1950) score, a strictly proper
rule (Gneiting & Raftery 2007), and report skill relative to climatology. §6.3
formalizes a limitation of unweighted proper scores under extreme class
imbalance that connects to the literature on rare-event verification and
weighted scoring (e.g., Ferro & Stephenson 2011): propriety guarantees honest
elicitation, not sensitivity to refinements of small-mass classes.

## 3. Data

All inputs are public. The system merges nine sources onto a common spine —
Gleditsch–Ward (G-W) country code × year (Gleditsch & Ward 1999) — with
year-aware crosswalks and a validation gate; the merged product is
redistributed under CC BY 4.0 as `tocsin-dataset-26.1` with a full codebook.

- **UCDP/PRIO** (release 26.1): the Armed Conflict Dataset and its dyadic
  version (Gleditsch et al. 2002; Davies et al. 2026), the Georeferenced
  Event Dataset (Sundberg & Melander 2013) with monthly *candidate* updates,
  non-state and one-sided tables, and the termination/episode coding of
  Kreutz (2010). Events with UCDP placeholder actors are excluded from dyad
  grain; candidate files are deduplicated by event id with latest-version
  precedence.
- **Gleditsch–Ward** system membership and minimum distances (Gleditsch &
  Ward 2001), defining state-system exposure and the ≤400 km proximity
  relation.
- **PRIO Battle Deaths v3.1** (Lacina & Gleditsch 2005), extending
  state-based death series to 1946 for descriptive use.
- **Powell–Thyne coups** (Powell & Thyne 2011): 1950–present attempts and
  outcomes.
- **V-Dem Regimes of the World** (Lührmann, Tannenberg & Lindberg 2018), via
  Our World in Data.
- **OWID population** (UN WPP/HYDE composite), carried forward to the data
  edge.
- **World Bank WDI** covariates (income, inflation, age structure,
  urbanization, infant mortality; CC BY 4.0).
- **Ethnic Power Relations 2021** (Vogt et al. 2015): politically excluded
  population shares.
- **Correlates of War**: dyadic militarized interstate disputes 4.03 (Maoz et
  al. 2019; Palmer et al. 2022), National Material Capabilities v7 (Singer,
  Bremer & Stuckey 1972), and Formal Alliances v4.1 (Gibler 2009), with a
  unit-tested COW→G-W crosswalk (unified Germany 255→260, Yemen 679→678,
  Serbia via the year-aware 345→340 alias, and the Pacific microstates
  remapped simultaneously).

Two engineered universes matter below. The **country universe** counts
main-system G-W members (12,703 country-years, 1946–2025). The **pair
universe** operationalizes politically relevant pairs as proximity (≤400 km) ∪
same-region ∪ P5-membership: 243,609 undirected pair-years, within which
98.2% of all UCDP state-based dyadic activity occurs — constructed *ex ante*,
never by conditioning on observed conflict.

## 4. The engine

### 4.1 Estimand and reference classes

For a unit *u* (country, dyad, or pair), year *t*, and measure *m* (deaths
above a threshold; UCDP activity; episode termination; coup attempt), the
engine estimates P(*m* holds for *u* in *t*) as a shrunk historical frequency
over a reference class defined entirely by *recency structure* observable
before *t*:

- **Active units** are banded by episode age (consecutive hit-years: 1, 2–3,
  4–9, 10+) × last-year intensity (below/above the UCDP war line of 1,000
  deaths; for coups, failed/successful).
- **Non-active units** are banded by time since last hit (*recent* 2–3,
  *dormant* 4–10, *cold* 11+/never), with a spatial-contagion flag (+nbr) when
  any ≤400 km neighbor was in state-based conflict the prior year.
- At month grain, active units additionally carry a **tempo band** (trailing
  hit-months 1–3, 4–8, 9–12), and windows that are not calendar-aligned are
  priced on a rolling monthly substrate whose bucket construction provably
  reduces to the annual engine's for January-aligned windows.

### 4.2 Estimation

Within bucket *b* at level ℓ ∈ {self, region, global}, with *k* hits in *n*
class-years, the class rate is the Jeffreys-smoothed frequency
p̂ = (k + ½)/(n + 1). Levels are combined by empirical-Bayes shrinkage
(Efron & Morris 1975): the self-level posterior is

  p̃_self = (k_self + M · p̂_parent) / (n_self + M),

with the prior strength *M* moment-matched from the dispersion of class rates
across units and clamped to [5, 1000]; regions falling below 30 class-years
fall back to the global class. The headline probability is the deepest level
with adequate support, and every output ships the full ladder — counts,
rates, *M*, and posterior at each level — plus caveat notes (left-censoring
at the substrate edge, window approximations, provisional-data flags).

### 4.3 Walk-forward evaluation

All evaluation is walk-forward: scoring year *t* uses classes built from data
strictly before *t* (five-year burn-in), so every reported score is
out-of-sample by construction. A class-signature memoization makes the full
seven-suite backtest (≈290,000 unit-year records) run in seconds, which is
what renders the preregistration protocol of §5 practical. Current
walk-forward performance (Brier; skill = 1 − Brier/Brier_climatology):

| suite | n | base rate | Brier | skill |
|---|---:|---:|---:|---:|
| country, sb deaths ≥25 | 5,547 | .167 | .0411 | +70.6% |
| country, all-type deaths ≥100 | 5,547 | .160 | .0366 | +72.8% |
| country, UCDP activity | 11,274 | .170 | .0495 | +65.0% |
| dyad, UCDP activity | 24,876 | .115 | .0405 | +60.6% |
| dyad, episode termination | 2,797 | .234 | .1668 | +7.1% |
| pair, onset/activity | 234,136 | .0006 | .0005 | +19.6% |
| country, coup attempt | 6,145 | .019 | .0197 | +17.6% |

Two design decisions were themselves settled empirically and are kept as
negative results: horizon-aware class decay (pricing a forecast *g* years past
the data edge by class rates offset *g*) measured *worse* (+.003 Brier;
class-level decay pools exiting with persisting units), so one-step rates are
applied frozen; and a promote-only nowcast lets provisional current-year data
upgrade but never downgrade a bucket.

## 5. The arena: scoring against the state of the art

### 5.1 Design

We score all systems on VIEWS's native target — P(≥25 state-based battle
deaths in a country-month), UCDP best estimate — at each of five historical
vantages (VIEWS `fatalities002` runs of April and October 2023, April and
October 2024, April 2025), horizons 1–12 months, using only information
available at each vantage. TOCSIN runs walk-forward-clamped (classes end at
the vantage). The VIEWS probability is its published `main_dich`, whose
semantics we verified empirically rather than assumed: across pre-2024 runs
its mean (.138) matches the realized ≥25 frequency (.136), not the ≥1
frequency (.251). Baselines: **persistence** (country's trailing-12-month hit
rate, add-one smoothed) and **climatology** (full-history monthly rate,
Jeffreys-smoothed). 7,680 scored country-months; 7% of outcomes are
provisional (candidate GED) at scoring time.

### 5.2 Results

| model | Brier | skill vs clim. | h1–3 | h4–6 | h7–12 |
|---|---:|---:|---:|---:|---:|
| **pool: VIEWS + persistence** | **.03987** | **+56.8%** | .0340 | .0376 | .0439 |
| pool: all three | .04087 | +55.7% | .0354 | .0382 | .0450 |
| VIEWS | .04123 | +55.3% | .0337 | .0396 | .0458 |
| persistence | .04326 | +53.1% | .0389 | .0401 | .0471 |
| TOCSIN | .04610 | +50.0% | .0413 | .0425 | .0503 |
| climatology | .09219 | 0 | .0877 | .0929 | .0940 |

Three readings, before the pools (which we defer to §7):

1. **The transparency tax is ~12%.** A pure lookup table — auditable to the
   class counts — concedes .0049 Brier to a covariate-rich ML ensemble on the
   ensemble's home target. Half of an initially larger gap was closed by a
   single recency-structure refinement (the tempo band moved TOCSIN from
   .0611 to .0461), i.e., by *better history*, not covariates.
2. **The baseline embarrassment replicates.** Persistence sits within 5% of
   VIEWS. This is an independent reproduction, on a fixed public target with
   verified semantics, of the pattern Cederman and Weidmann (2017) warned
   about.
3. **Aggregate and disaggregate disagree.** TOCSIN produces the better
   forecast in 5,386 of 7,657 decided country-months (70%) yet loses on
   aggregate: it wins small on the quiet mass and pays large on transitions,
   the fingerprint of a system whose errors concentrate exactly where VIEWS's
   covariates earn their keep. The horizon decomposition agrees: the deficit
   is largest at h1–3 (.0413 vs .0337), where fresh signal matters most, and
   smallest at h7–12 (.0503 vs .0458).

We refrain from formal tests of Brier differences: the 7,680 records are
strongly dependent (overlapping 12-month horizons from five vantages;
within-country serial correlation), and a clustered Diebold–Mariano treatment
on five effective vantages would be underpowered theater. The differences we
interpret — pools versus singles, and the covariate nulls below — are either
zero-parameter comparisons or preregistered decisions, not significance
claims.

## 6. The covariate program: five preregistered failures

### 6.1 The tune/validate protocol

Walk-forward evaluation removes look-ahead but not *designer overfitting*: a
researcher who iterates conditioning schemes against the full scored history
is fitting to it. After one such episode — a V-Dem regime conditioning that
looked plausible and measured worse on every country suite (e.g., sb≥25
.0411→.0413; all-type≥100 .0366→.0371) — we froze a protocol:

1. Split scored years at 2007: **tune** (≤2007), **validate** (>2007).
2. Candidate schemes are enumerated *a priori*; any thresholds are computed
   from tune-era data only.
3. Candidates compete on tune; the winner is compared to baseline on validate
   **exactly once**.
4. Adoption requires ≥1% relative Brier improvement on validate *and* a
   consistency guard on tune (a majority of cuts helping, for parametric
   families; the winner itself beating baseline, for heterogeneous sets).
5. Every consultation of validate is logged; when an era's validate set has
   been consulted for a family of hypotheses, it is **retired** — subsequent
   studies require genuinely fresh outcome years.

The 1% bar was set before any study ran, calibrated to the observed
noise scale of the validate split (a scheme that lost on tune still swung
+0.4% on validate; see below). The protocol's output is a verdict, not a
p-value; its epistemic content is that validate data cannot be shopped.

### 6.2 Results

**Study 1 — youth bulges (country grain).** Descriptively, age structure is
the strongest single onset covariate we measured: among 6,280 currently-quiet
country-years with covariate coverage (base onset rate 3.3%), those with >39%
of population under 14 onset at 6.5% versus 1.7% for older populations — a
~4× lift, consistent with Urdal (2006). Under the protocol (candidate cuts at
the 50th/60th/66th/75th tune-era percentiles): **zero of four cuts beat the
baseline engine on tune** (best .05384 vs .0537); the least-bad cut carried a
+0.4% relative edge to validate — below the bar, and with the tune guard
failed. **Rejected.** A naive adoption threshold (ΔBrier < −.0001) would have
adopted a covariate that could not beat its own tuning baseline; the guard
exists precisely for this case.

**Study 2 — dispute and alliance history (pair grain).** Four candidates on
the pair universe: any militarized-dispute history (ever-MID), MID within 25
years, fatal-MID history, and a defense-pact flag (COW alliances, last
observed status carried forward). Descriptively the leading candidate is
enormous: among pair-years entering the *cold* bucket, those with MID history
onset at 0.194% (44/22,649) versus 0.006% (14/215,855) without — a **30×**
class-rate ratio. Under the protocol: **zero of four candidates beat baseline
on tune** (.000574 vs .000573); the tune-selected candidate (ever-MID) was
0.7% relatively *worse* on validate. **Rejected** — for a reason §6.3 shows is
structural rather than empirical.

**Study 3 — exclusion and the joint hypothesis (country grain; final
consultation of the 2007 era).** The one descriptively motivated interaction
not yet tested: ethnic exclusion alone, youth∧exclusion (the compound cell
onsets at 8.6% versus 2.9% for older/low-exclusion years), and youth∨exclusion
— deliberately two-cell flags rather than fragmenting cross-products. **Zero
of three beat baseline on tune**; the tune-selected candidate (exclusion
alone) was 1.0% relatively worse on validate — the worst held-out reading of
any study. **Rejected**, and the 2007 validation era was retired as
preregistered (country validate consulted twice, pair once).

Together with the two pre-protocol ablations (regime conditioning; horizon
decay), the scoreboard is **five families proposed, five rejected**, while
the engine's own recency refinements (episode age, intensity, tempo,
neighbor) were adopted on the same walk-forward evidence. The pattern is not
that structural covariates are uninformative — descriptively they are strong
— but that they are informative *about the same thing recency already
measures*. A young, exclusionary state that has been at peace for thirty
years is, empirically, at low risk; a middle-aged democracy one year out of
civil war is not. Conflict history is not a proxy to be improved upon; it is
the sufficient statistic the covariates approximate.

Two mechanisms recur. **Absorption**: conditional on bucket, the covariate's
class-rate difference shrinks toward zero (youth's 4× marginal lift is
mostly the young-countries-fight-recently composition effect). **Fragmentation
under shrinkage**: splitting a bucket cuts class support; moment-matched
shrinkage then pulls both children toward the parent, so even a real
difference buys little resolution while adding estimator variance — the
measured regime failure, and the reason the joint study used two-cell flags.
The third mechanism deserves its own subsection.

### 6.3 Metric blindness at rare-event base rates

The pair-grain rejection is *not* evidence that dispute history is
uninformative — the 30× class ratio is real and walk-forward. It is evidence
about the scoring rule. Decompose the maximum possible Brier improvement from
any refinement of a class with pooled rate p̄ into subclasses c with masses
w_c and true rates π_c (this is the resolution term of Murphy's
decomposition):

  ΔBrier_max = Σ_c w_c (π_c − p̄)².

For the cold-pair class (238,504 pair-years entering *cold*): w₁ = 0.095,
π₁ = .00194; w₀ = 0.905, π₀ = .000065; p̄ = .000243. Then
ΔBrier_max = 0.095·(.00170)² + 0.905·(.00018)² ≈ 3.0×10⁻⁷ — **0.05% of the
.000573 tune-era baseline**, twenty times below the preregistered 1% bar. At these base rates, *perfect* conditioning is invisible to aggregate
Brier: the quiet mass is already scored nearly perfectly, and the flagged
class is too small for its (large, real) improvement to register. The same
arithmetic explains why the engine's 7× neighbor-contagion signal barely
moves month-grain Brier, and why pair-grain skill (+19.6%) looks modest
despite genuine discrimination.

The methodological point generalizes: **strictly proper scores guarantee
honest elicitation, not sensitivity to policy-relevant refinements under
extreme class imbalance.** A field that selects covariates by aggregate Brier
on rare-event targets will systematically discard its strongest onset
signals. Candidate remedies — weighted proper scores (Ferro & Stephenson
2011), log score (which diverges precisely where Brier saturates), or
class-conditional evaluation — must be *preregistered*, because switching
metrics after observing results reintroduces the shopping the protocol
exists to prevent. In our own system the verdict stands (the era is spent);
the 30× signal ships as displayed context on pair forecasts, labeled as
having failed the adoption bar. A log-loss bar for the pair grain is
preregistered here for the next evaluation era (outcome years ≥2026).

## 7. Pooling: the best forecast is nobody's model

The head-to-head structure of §5.2 — TOCSIN better on 70% of months, worse on
aggregate — is the textbook precondition for combination gains: the systems'
errors are differently shaped. We therefore score equal-weight linear opinion
pools. Equal weights involve zero fitted parameters, so scoring them on the
same vantages is measurement, not tuning; the adoption criterion (beat the
best member) was fixed in advance, and all four candidate pools are reported.

| pool | Brier | vs best single |
|---|---:|---:|
| VIEWS + persistence | **.03987** | **−3.3%** |
| VIEWS + persistence + TOCSIN | .04087 | −0.9% |
| VIEWS + TOCSIN | .04144 | +0.5% |
| persistence + TOCSIN | .04329 | +5.0% |

Two results. First, the field's cheapest available accuracy gain on this
target is not a model at all: averaging the ML system with naive persistence
beats everything, at every horizon band, for free. This is the Bates–Granger
result landing in the conflict domain with unusual force, and it should
discipline how single-model improvements are marketed: a new system that does
not beat the *pool* has not advanced the frontier.

Second, the pool is a diagnostic instrument. Adding TOCSIN to
VIEWS+persistence *worsens* it (.03987→.04087) despite TOCSIN's 70% month-wise
win rate, and TOCSIN+persistence is barely better than persistence alone. The
inference is sharp: at month grain, TOCSIN's forecast is (approximately) a
recalibrated persistence — its information is already inside the pool, so it
adds redundancy, not diversity. Pools pay for *orthogonal* error, and VIEWS's
covariate machinery is the orthogonal ingredient. This reframes the
transparency tax of §5.2: the transparent system's residual value on this
target is not incremental accuracy (persistence supplies its signal more
cheaply) but auditability — and its *distinct* value lies on targets no other
system prices, to which we return below.

## 8. Discussion

**A deflationary synthesis.** Assembled, the results argue that the standard
country-month occurrence target is close to its practical predictability
ceiling: (i) a pure recency machine reaches within 12% of the state of the
art; (ii) naive persistence reaches within 5%; (iii) five theoretically
central covariate families add nothing out-of-sample once recency is
conditioned on; (iv) the cheapest remaining gain is a zero-parameter average.
None of this says conflict is unpredictable — skill versus climatology is
+50–57% throughout — it says the *predictable part is mostly history*, and
that the marginal covariate, however strong its bivariate association, is
purchasing information the forecast already owns. This is Cederman and
Weidmann's (2017) caution, converted from warning into measurement.

**What transparency bought.** The auditable design is not (on this target) an
accuracy strategy; it is an epistemics strategy. Because every probability
decomposes into named classes and counts, failures localize: we can state
*why* youth fails (absorption), why regime fails (fragmentation), why
dispute history fails (metric blindness) — mechanisms, not shrugs. The same
architecture made the preregistration protocol cheap enough to actually
follow, and the negative results reportable at publication grade. We suggest
the field's forecasting systems adopt adoption-protocols of this shape:
enumerated candidates, tune/validate separation, single consultation,
retirement of spent eras, and published rejections.

**Rare events need preregistered metrics.** §6.3's decomposition implies that
aggregate Brier is the wrong adoption criterion wherever base rates are far
from the forecast probabilities' working range — dyadic onset, interstate
war, mass-atrocity onset. Weighted or logarithmic criteria see what Brier
cannot, but only preregistration keeps them honest.

**Limitations.** (1) The arena scores one target at one grain — VIEWS's home
turf; TOCSIN's design center (annual horizons, arbitrary thresholds,
termination, coups — the operational questions in its journal) has no
external comparator yet, and our claims are correspondingly scoped. (2) Five
vantages with overlapping horizons preclude meaningful significance testing
on Brier differences; our decisive comparisons are zero-parameter or
preregistered instead. (3) Seven percent of arena outcomes were provisional
(candidate GED) at scoring time; UCDP revisions could shift third-decimal
values. (4) VIEWS is represented by its published dichotomous output under
empirically verified semantics; other VIEWS surfaces (expected fatalities)
are not evaluated. (5) The covariate verdicts are specific to this engine's
conditioning structure and adoption bar; they bound the *increment over
recency*, not the covariates' scientific relevance. (6) The 2007-split era is
spent; our own future covariate work must wait for fresh outcome years, and
we commit here to the preregistered log-loss bar for the pair grain.

**Future work.** The deployed system accumulates the missing evidence
automatically: a journal of operational forecasts resolves monthly against
UCDP updates, building both an annual-grain arena on TOCSIN's own targets and
the fresh validation era (outcomes ≥2026) that the next covariate — a
continuous tempo input aimed at the measured h1–3 deficit — must clear. The
combination result suggests a standing published pool alongside; the metric
result suggests the community converge on preregistered rare-event scoring
before, not after, the next generation of systems reports its gains.

## 9. Reproducibility

Everything is public. Code (MIT) and the merged dataset (CC BY 4.0, with
per-source attribution chains and codebook) are at
github.com/KaraZajac/TOCSIN; the live system, including the arena table, all
walk-forward calibration diagnostics, and every forecast with its full
reference-class ladder, is at tocsin.karazajac.io. A single command
(`tocsin pull && tocsin build && tocsin backtest && tocsin benchmark`)
regenerates every number in this paper from primary sources; the
preregistration protocol is `tocsin protocol`. The five-vantage arena pins
the exact VIEWS runs consumed. Raw ACLED data informs a display-only
divergence indicator on the site and is neither redistributed nor used in
any result reported here.

## Acknowledgments

The system was designed, built, and audited by the author in an intensive
pair-collaboration with an AI assistant (Claude, Anthropic), which drafted
code and this manuscript under the author's direction; all design decisions,
verdicts, and errors are the author's. The author thanks the maintainers of
UCDP, VIEWS, the Correlates of War project, V-Dem, EPR, PRIO, Powell &
Thyne, Gleditsch & Ward, Our World in Data, and the World Bank for decades
of public data stewardship.

## References

*(Working list — verify page numbers and finalize formatting before
submission.)*

Bates, J. M., & Granger, C. W. J. (1969). The combination of forecasts.
*Operational Research Quarterly*, 20(4), 451–468.

Blair, R. A., & Sambanis, N. (2020). Forecasting civil wars: Theory and
structure in an age of "big data" and machine learning. *Journal of Conflict
Resolution*, 64(10), 1885–1915.

Brier, G. W. (1950). Verification of forecasts expressed in terms of
probability. *Monthly Weather Review*, 78(1), 1–3.

Cederman, L.-E., & Weidmann, N. B. (2017). Predicting armed conflict: Time to
adjust our expectations? *Science*, 355(6324), 474–476.

Cederman, L.-E., Wimmer, A., & Min, B. (2010). Why do ethnic groups rebel?
New data and analysis. *World Politics*, 62(1), 87–119.

Chadefaux, T. (2017). Conflict forecasting and its limits. *Data Science*,
1(1–2), 7–17.

Clemen, R. T. (1989). Combining forecasts: A review and annotated
bibliography. *International Journal of Forecasting*, 5(4), 559–583.

Colaresi, M., & Mahmood, Z. (2017). Do the robot: Lessons from machine
learning to improve conflict forecasting. *Journal of Peace Research*, 54(2),
193–214.

Collier, P., & Hoeffler, A. (2004). Greed and grievance in civil war. *Oxford
Economic Papers*, 56(4), 563–595.

Davies, S., Engström, G., Pettersson, T., & Öberg, M. (2026). Organized
violence 1989–2025 (UCDP annual update). *Journal of Peace Research*, 63(4).

Dawes, R. M. (1979). The robust beauty of improper linear models in decision
making. *American Psychologist*, 34(7), 571–582.

Efron, B., & Morris, C. (1975). Data analysis using Stein's estimator and its
generalizations. *Journal of the American Statistical Association*, 70(350),
311–319.

Fearon, J. D., & Laitin, D. D. (2003). Ethnicity, insurgency, and civil war.
*American Political Science Review*, 97(1), 75–90.

Ferro, C. A. T., & Stephenson, D. B. (2011). Extremal dependence indices:
Improved verification measures for deterministic forecasts of rare binary
events. *Weather and Forecasting*, 26(5), 699–713.

Gibler, D. M. (2009). *International Military Alliances, 1648–2008*. CQ Press.

Gleditsch, K. S., & Ward, M. D. (1999). Interstate system membership: A
revised list of the independent states since 1816. *International
Interactions*, 25(4), 393–413.

Gleditsch, K. S., & Ward, M. D. (2001). Measuring space: A minimum-distance
database and applications to international studies. *Journal of Peace
Research*, 38(6), 739–758.

Gleditsch, N. P., Wallensteen, P., Eriksson, M., Sollenberg, M., & Strand, H.
(2002). Armed conflict 1946–2001: A new dataset. *Journal of Peace Research*,
39(5), 615–637.

Gneiting, T., & Raftery, A. E. (2007). Strictly proper scoring rules,
prediction, and estimation. *Journal of the American Statistical
Association*, 102(477), 359–378.

Goldstone, J. A., Bates, R. H., Epstein, D. L., Gurr, T. R., Lustik, M. B.,
Marshall, M. G., Ulfelder, J., & Woodward, M. (2010). A global model for
forecasting political instability. *American Journal of Political Science*,
54(1), 190–208.

Hegre, H., Allansson, M., Basedau, M., et al. (2019). ViEWS: A political
violence early-warning system. *Journal of Peace Research*, 56(2), 155–174.

Hegre, H., Bell, C., Colaresi, M., et al. (2022). Lessons from an escalation
prediction competition. *International Interactions*, 48(4), 521–554.

Kahneman, D., & Lovallo, D. (1993). Timid choices and bold forecasts: A
cognitive perspective on risk taking. *Management Science*, 39(1), 17–31.

Kreutz, J. (2010). How and when armed conflicts end: Introducing the UCDP
Conflict Termination dataset. *Journal of Peace Research*, 47(2), 243–250.

Lacina, B., & Gleditsch, N. P. (2005). Monitoring trends in global combat: A
new dataset of battle deaths. *European Journal of Population*, 21(2–3),
145–166.

Lührmann, A., Tannenberg, M., & Lindberg, S. I. (2018). Regimes of the World
(RoW): Opening new avenues for the comparative study of political regimes.
*Politics and Governance*, 6(1), 60–77.

Makridakis, S., & Hibon, M. (2000). The M3-competition: Results,
conclusions and implications. *International Journal of Forecasting*, 16(4),
451–476.

Maoz, Z., Johnson, P. L., Kaplan, J., Ogunkoya, F., & Shreve, A. (2019). The
dyadic militarized interstate disputes (MIDs) dataset version 3.0. *Journal
of Conflict Resolution*, 63(3), 811–835.

Meehl, P. E. (1954). *Clinical versus Statistical Prediction*. University of
Minnesota Press.

Muchlinski, D., Siroky, D., He, J., & Kocher, M. (2016). Comparing random
forest with logistic regression for predicting class-imbalanced civil war
onset data. *Political Analysis*, 24(1), 87–103.

Palmer, G., McManus, R. W., D'Orazio, V., et al. (2022). The MID5 dataset,
2011–2014: Procedures, coding rules, and description. *Conflict Management
and Peace Science*, 39(4), 470–482.

Powell, J. M., & Thyne, C. L. (2011). Global instances of coups from 1950 to
2010: A new dataset. *Journal of Peace Research*, 48(2), 249–259.

Singer, J. D., Bremer, S., & Stuckey, J. (1972). Capability distribution,
uncertainty, and major power war, 1820–1965. In B. Russett (Ed.), *Peace,
War, and Numbers* (pp. 19–48). Sage.

Sundberg, R., & Melander, E. (2013). Introducing the UCDP georeferenced event
dataset. *Journal of Peace Research*, 50(4), 523–532.

Timmermann, A. (2006). Forecast combinations. In G. Elliott, C. W. J.
Granger, & A. Timmermann (Eds.), *Handbook of Economic Forecasting* (Vol. 1,
pp. 135–196). Elsevier.

Urdal, H. (2006). A clash of generations? Youth bulges and political
violence. *International Studies Quarterly*, 50(3), 607–629.

Vesco, P., Hegre, H., Colaresi, M., et al. (2022). United they stand:
Findings from an escalation prediction competition. *International Journal of
Forecasting*, 38(4), 1521–1540.

Vogt, M., Bormann, N.-C., Rüegger, S., Cederman, L.-E., Hunziker, P., &
Girardin, L. (2015). Integrating data on ethnicity, geography, and conflict:
The Ethnic Power Relations dataset family. *Journal of Conflict Resolution*,
59(7), 1327–1342.

Ward, M. D., Greenhill, B. D., & Bakke, K. M. (2010). The perils of policy by
p-value: Predicting civil conflicts. *Journal of Peace Research*, 47(4),
363–375.
