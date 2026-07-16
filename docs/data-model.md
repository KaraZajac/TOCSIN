# Data model

## sources/ (gitignored, regenerable)

`wopr pull` scrapes ucdp.uu.se/downloads once to discover the newest annual
release and the current candidate-GED monthly files, then fetches:

| file | dataset |
|---|---|
| `ucdp-prio-acd.csv` | UCDP/PRIO Armed Conflict Dataset (conflict-year, 1946–) |
| `ucdp-dyadic.csv` | UCDP Dyadic ACD (dyad-year) |
| `ucdp-ged.csv` | UCDP GED (event level, 1989–) |
| `ucdp-nonstate.csv`, `ucdp-onesided.csv` | non-state conflict, one-sided violence (year grain) |
| `ucdp-cy.csv` | official organized-violence country-year aggregates |
| `candidate/GEDEvent_*.csv` | preliminary monthly events past the annual cutoff |
| `gw-iisystem.dat`, `gw-microstates.dat` | Gleditsch–Ward state system |
| `manifest.yaml` | release + download timestamps |

Candidate files overlap and correct each other; consumers dedupe by event id
(latest file version wins) and drop dates at or before the annual cutoff.
UCDP id 345 (Serbia (Yugoslavia)) maps to G-W 340 from 2007 (`build.to_gw`).

### sources/acled/ (optional; `wopr acled`)

With `ACLED_USERNAME`/`ACLED_PASSWORD` in the repo-root `.env`,
`wopr acled` logs into myACLED (Drupal session), discovers the current
aggregate file behind each `/aggregated/…` landing page (upstream filenames
change per release), and converts the xlsx to CSV with a stdlib reader:

- `pv-country-month.csv` — political-violence events by country-month (2017–)
- `pv/demos/fatalities/civilian-*.csv` — country-year series
- `weekly-<region>.csv` — week × Admin-1 events, fatalities, population
  exposure (updated weekly; the `WEEK` column is an Excel date serial)

Caveats: ACLED's ontology (battles, explosions/remote violence, violence
against civilians; all reported fatalities) is not UCDP's sb/ns/os with a
25-death rule — treat these as tempo signals and cross-checks, not resolution
authorities for UCDP-pinned questions. The event-level read API
(`wopr acled --api-check`, OAuth bearer via `wopr.pipeline.acled.api_read`)
requires a myACLED access level above the automatic *Open* tier.

## data/ (committed, rebuilt by `wopr build`)

- `meta.yaml` — release, `annual_coverage_end` (last authoritative date),
  `data_through` (last candidate-covered date), row counts.
- `registry/states.yaml` — gwno, name, UCDP region, microstate flag, system
  spells (`to: null` = ongoing).
- `registry/conflicts.yaml` — UCDP conflict id, name, type, incompatibility,
  region(s), location countries, active years.
- `registry/dyads.yaml` — state-based dyads; `acd: false` marks dyads that
  only ever appear sub-threshold in GED.
- `registry/nonstate.yaml`, `registry/onesided.yaml` — same idea for the
  other two violence categories.
- `tables/country-year.csv` — one row per G-W state-year 1946–present:
  `acd_intensity` (0/1/2), and official sb/ns/os best-estimate deaths from
  1989. Microstates carry `main_system=0` and are excluded from engine
  denominators.
- `tables/dyad-year.csv` — state-based dyad-years: ACD intensity plus GED
  event/death sums (rows exist for sub-threshold GED activity too).
- `tables/country-month.csv`, `tables/dyad-month.csv` — 1989–present monthly
  grain including candidate months; `provisional=1` rows are candidate-based
  and get rebuilt/confirmed on the next release. Dyad-month excludes
  candidate events with placeholder (XXX) attribution.

## questions/ (committed — the journal)

One YAML per question, `YYYY-NNN-slug.yaml`:

```yaml
id: 2026-004
title: "Ethiopia–Eritrea: interstate violence in 2026"
question: Will UCDP record ≥25 battle-related deaths (best estimate,
  state-based) in the dyad Government of Eritrea - Government of Ethiopia
  between 2026-01-01 and 2026-12-31 inclusive?
created: '2026-07-16T04:00:00Z'
status: open            # open | resolved | void
criteria:
  scope: {kind: dyad, id: 865, name: Government of Eritrea - Government of Ethiopia}
  types: [sb]           # GED type_of_violence subset: sb/ns/os
  measure: deaths       # deaths | events
  threshold: 25
  window: {start: '2026-01-01', end: '2026-12-31'}
resolution_policy: {method: auto}   # auto-graded from the data
prior:                  # the outside view, stored at creation
  p: 0.0048
  computed: '2026-07-16T04:00:00Z'
  engine: 0.1.0
  detail: {…full ladder…}
forecasts:              # the inside view, appended over time
  - {t: '2026-07-16T04:05:00Z', p: 0.03, note: "border rhetoric worse than base rate implies"}
resolution:             # written by `wopr resolve`
  outcome: no
  decided_on: '2026-12-31'
  provisional: true     # leaned on candidate data; confirmed next release
  basis: {release: '26.1', total: 4, events: 2, excluded_unattributed: 0}
```

Resolution semantics: **yes** the moment the cumulative measure crosses the
threshold inside the window (`decided_on` = crossing date); **no** once the
window is fully covered by available data; otherwise pending. Provisional
resolutions are re-graded after each annual release and can flip (with a
note — and the score moves accordingly).
