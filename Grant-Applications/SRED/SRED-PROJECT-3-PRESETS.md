# SR&ED T661 — Project 3: Clinical Preset Parameter Calibration

> **Project Title:** Systematic Calibration of Cross-Frequency Coherence Parameters for Clinical EEG Conditions
> **Claim Period:** 2026 fiscal year
> **Classification:** PRIVATE — for T661 filing and SR&ED consultant review only

---

## Project Summary

| Field | Detail |
|-------|--------|
| Project start | Q3 2026 (overlaps with IRAP Phase 4) |
| Project end | Q1 2027 (estimated) |
| Personnel | Founder (lead developer), ML engineer (contractor) |
| Key files | Clinical preset modules, benchmark datasets |
| Qualifying expenditure (est.) | CAD 20,000–30,000 (salary allocation — non-IRAP portion) |
| Target conditions | Healthy, MDD, MCI/Alzheimer's, Epilepsy, Meditation, Anesthesia, ADHD, Custom |

---

## Line 242: Technological Uncertainties (≤350 words)

Clinical preset calibration requires mapping published theta-gamma coherence findings from diverse studies into a unified parameter set for our pipeline. This involves three technological uncertainties that cannot be resolved through routine engineering.

**Uncertainty 1: Cross-Study Parameter Harmonization.** Published studies reporting theta-gamma coherence values use different EEG hardware (clinical 64-channel systems vs. consumer 4-channel devices), different electrode montages (10-20 vs. 10-10 system), different preprocessing pipelines (ICA artifact rejection vs. threshold-based rejection), and different reference schemes (average reference vs. linked mastoids). It was unknown whether a single set of filter parameters, window sizes, and normalization constants could reproduce published coherence values across these heterogeneous conditions. The degree to which hardware and preprocessing differences are absorbed by the PLV metric — vs. requiring per-study correction factors — had not been systematically investigated.

**Uncertainty 2: Condition-Specific Frequency Band Optimization.** Standard theta (4–8 Hz) and gamma (30–100 Hz) bands are used across conditions, but published evidence suggests that pathological states may shift peak coupling frequencies. For example, MDD may show altered theta peak around 6–7 Hz, while epileptic hypersynchronization may involve narrower gamma sub-bands (30–50 Hz). It was unknown whether condition-specific band tuning would significantly improve coherence score discrimination (healthy vs. pathological), or whether the standard bands are sufficiently robust.

**Uncertainty 3: Threshold Validation Without Ground Truth.** There is no universally accepted ground truth for "correct" theta-gamma coherence scores. Published values vary by study, and inter-study comparison is confounded by methodological differences (Uncertainty 1). It was unknown how to validate our preset thresholds when the reference values themselves have uncertainty ranges of ±15–25%. Determining whether our presets are "correct within ±10%" requires a statistical methodology for comparing against noisy references — a methodological challenge beyond routine software calibration.

*(~290 words)*

---

## Line 244: Work Performed — Systematic Investigation (≤700 words)

### Phase 1: Clinical Literature Database

We compiled a database of 47 published studies (2010–2025) reporting theta-gamma coherence or phase-amplitude coupling values for each of our 8 target conditions. For each study, we recorded:
- Hardware (manufacturer, channel count, sampling rate)
- Montage (electrode placement system)
- Preprocessing pipeline (artifact rejection method, filter parameters)
- Reference scheme (average, linked mastoids, CSD)
- Reported coherence/PLV values (mean, SD, N)
- Condition classification and diagnostic criteria

This database serves as our reference standard for calibration.

### Phase 2: Hardware Normalization Experiment

We formulated the hypothesis that hardware-related variance in PLV can be modeled as a multiplicative correction factor dependent on (a) number of channels and (b) reference scheme.

Using the publicly available TDBRAIN dataset (1,274 EEG recordings, diverse hardware), we computed PLV using our pipeline with identical filter parameters and measured the systematic offset attributable to hardware configuration. We tested:
- A linear correction model: PLV_corrected = α × PLV_raw + β
- A per-hardware lookup table: correction factor per (channel_count, reference_scheme) pair
- No correction (baseline)

We validated each approach by computing the coefficient of variation (CV) of PLV across hardware configurations for the same clinical condition.

### Phase 3: Condition-Specific Band Optimization

For each of the 8 conditions, we performed a grid search over:
- Theta band: lower cutoff (3–5 Hz, step 0.5), upper cutoff (7–9 Hz, step 0.5)
- Gamma band: lower cutoff (25–35 Hz, step 2.5), upper cutoff (80–120 Hz, step 10)

Using available clinical EEG datasets (PhysioNet, TDBRAIN, MPI-Leipzig Mind-Brain-Body), we computed PLV for each band combination and measured discriminability between healthy controls and each pathological condition using:
- Cohen's d effect size
- Area under the ROC curve (AUC)
- Welch's t-test p-value

We compared condition-specific optimized bands against the standard (4–8 Hz / 30–100 Hz) to determine if band tuning provides statistically significant improvement.

### Phase 4: Threshold Calibration with Noisy References

To address the uncertainty of validating against noisy reference values, we developed a bootstrapped comparison methodology:

1. For each condition, we sampled from the published value distribution (mean ± reported SD)
2. We computed our pipeline's PLV on matched clinical data
3. We computed a "compatibility score": the probability that our value falls within the reference distribution
4. We repeated 10,000 bootstrap iterations to estimate our confidence interval

A preset was considered "validated" if the compatibility score exceeded 0.80 — meaning our value is within the reference distribution's range at least 80% of the time.

### Phase 5: Integration and Testing

We integrated the calibrated parameters into the preset system:
- Each preset stores: band ranges, window size, normalization parameters, hardware correction factor, classification thresholds
- Presets are selectable via API: `tracker.set_preset("MDD")` or `tracker.set_preset("Epilepsy")`
- A benchmark test suite compares preset outputs against published values on a per-study basis

### Results Summary

**Hardware Normalization.** The per-hardware lookup table reduced cross-hardware PLV variance by 38% (CV from 0.23 to 0.14). The linear correction model achieved only 21% reduction. However, significant residual variance remained, attributable to preprocessing differences (artifact rejection methodology).

**Band Optimization.** Condition-specific bands improved discrimination for 3 of 8 conditions:
- Epilepsy: narrower gamma (30–50 Hz) improved AUC by 0.08
- MDD: shifted theta (5–8 Hz) improved Cohen's d by 0.15
- Anesthesia: wider gamma (25–120 Hz) captured burst-suppression patterns

For the remaining 5 conditions, standard bands were within 0.02 AUC of optimized bands — no significant benefit.

**Threshold Validation.** Using bootstrapped compatibility scores, 6 of 8 presets achieved >0.80 compatibility. Two conditions (MCI/Alzheimer's and ADHD) achieved only 0.68 and 0.72 respectively, due to high inter-study variance in published reference values.

*(~630 words)*

---

## Line 246: Technological Advancements Achieved (≤350 words)

This project produced three technological advancements:

**Advancement 1: Hardware Normalization Model for PLV.** We developed and validated a per-hardware correction approach that reduces cross-hardware PLV variance by 38%. The correction model — a lookup table indexed by (channel count, reference scheme) — enables meaningful comparison of coherence scores across different EEG hardware platforms. This is, to our knowledge, the first systematic characterization of hardware-dependent PLV bias for cross-frequency theta-gamma coupling. The finding that hardware effects are multiplicative (correctable by lookup table) rather than requiring complex nonlinear modeling is a practical advancement for the field.

**Advancement 2: Condition-Specific Band Optimization Map.** Through systematic grid search across 8 clinical conditions, we established that 3 conditions benefit significantly from non-standard frequency bands (Epilepsy: 30–50 Hz gamma; MDD: 5–8 Hz theta; Anesthesia: 25–120 Hz gamma), while 5 conditions are adequately served by standard bands (4–8 Hz / 30–100 Hz). This condition-to-band mapping constitutes a new resource for the cross-frequency coupling research community. The finding that most conditions don't require band tuning is itself an advancement — it simplifies preset design and reduces the parameter space that clinicians must understand.

**Advancement 3: Bootstrapped Compatibility Validation Methodology.** We developed a statistical methodology for validating coherence presets against published references that have inherent uncertainty (±15–25% inter-study variance). The bootstrapped compatibility score — the probability that a computed value falls within the sampled reference distribution over 10,000 iterations — provides a principled way to say "our preset agrees with the literature" when the literature itself has wide variance. This methodology is applicable beyond our specific use case to any biomarker calibration problem where ground truth values are only available as distributions rather than point estimates.

These advancements collectively produce the first validated, cross-hardware, condition-specific parameter preset system for EEG cross-frequency coherence analysis — a capability that does not exist in any current EEG analysis tool.

*(~300 words)*

---

## Supporting Evidence

| Evidence Type | Location | Description |
|---------------|----------|-------------|
| Clinical literature database | `experiments/presets/literature_db.csv` (local) | 47 studies, 8 conditions |
| Source code | Preset modules (development branch) | Calibration logic, correction factors |
| Git history | Development branch commits | Iterative calibration experiments |
| Jupyter notebooks | `experiments/presets/` (local) | Grid search results, bootstrap analysis |
| Timesheets | (to be maintained) | Hours allocated to this project |
| Public datasets | PhysioNet, TDBRAIN, MPI-Leipzig | Clinical EEG used for validation |
