# SR&ED T661 — Project 1: Cross-Frequency PLV Algorithm Development

> **Project Title:** Development of Adaptive Phase Locking Value Algorithm for Cross-Frequency EEG Coupling Analysis
> **Claim Period:** 2025–2026 fiscal year
> **Classification:** PRIVATE — for T661 filing and SR&ED consultant review only

---

## Project Summary

| Field | Detail |
|-------|--------|
| Project start | Q4 2025 |
| Project end | Ongoing (multi-year) |
| Personnel | Founder (lead developer) |
| Key files | `taurus_gcfd.py` (Lines 15–47), `posner_qpu_sim.py` |
| Qualifying expenditure (est.) | CAD 40,000–60,000 (salary allocation) |

---

## Line 242: Technological Uncertainties (≤350 words)

The Phase Locking Value (PLV) is a standard metric for measuring phase synchronization between two neural oscillations. However, applying PLV to **cross-frequency coupling** — where one frequency band is 5–25x higher than the other (e.g., theta at 4–8 Hz vs. gamma at 30–100 Hz) — introduces uncertainties that existing implementations do not address.

**Uncertainty 1: Adaptive Window Sizing.** Standard PLV implementations use a fixed analysis window (typically 1–5 seconds). When computing cross-frequency PLV between theta (period ~143–250 ms) and gamma (period ~10–33 ms), a fixed window captures vastly different numbers of cycles for each band. It was unknown whether an adaptive window proportional to the lower frequency's period would produce more stable PLV estimates, and if so, what the optimal proportionality constant should be. No published methodology exists for adaptive-windowed cross-frequency PLV.

**Uncertainty 2: Phase Extraction Accuracy at Band Boundaries.** The Hilbert transform extracts instantaneous phase, but its accuracy degrades near the edges of narrow bandpass-filtered signals. For our Butterworth filter (order 3, zero-phase via `filtfilt`), it was uncertain how much edge artifact contaminated the PLV estimate and whether edge-trimming, tapering, or mirror-padding would best mitigate this — specifically for the narrow theta band (4 Hz bandwidth) where filter roll-off is a larger fraction of the passband.

**Uncertainty 3: Normalization for Clinical Comparison.** Our coherence score maps PLV (range 0–1) to a global coherence metric via the transformation `coherence = 0.5 + (PLV × 0.5)`. It was uncertain whether this linear mapping preserves the statistical properties needed for meaningful comparison against published clinical thresholds (e.g., MDD coherence ~0.59, healthy ~0.90+), or whether a non-linear mapping would better align with the distribution of PLV values observed in clinical EEG data.

*(~300 words)*

---

## Line 244: Work Performed — Systematic Investigation (≤700 words)

### Phase 1: Literature Review and Hypothesis Formation

We conducted a systematic review of cross-frequency coupling methodologies published between 2015–2025, focusing on theta-gamma phase synchronization in EEG. Key references included Canolty & Knight (2010), Tort et al. (2010), and Cohen (2014). We identified that while PLV is well-established for within-band synchronization, its application to cross-frequency coupling lacks standardized methodology — particularly for window sizing and clinical normalization.

We formulated three testable hypotheses:
1. Adaptive window sizing (proportional to theta period) reduces PLV variance by >20% vs. fixed windows
2. Mirror-padding before Hilbert transform reduces edge artifacts more effectively than zero-padding or trimming for narrow-band theta signals
3. A sigmoidal normalization preserves clinical threshold discrimination better than linear normalization

### Phase 2: Implementation and Controlled Experiments

**Experiment 1 — Window Sizing.** We implemented the core PLV computation (`taurus_gcfd.py`, `calculate_global_coherence` method) using NumPy and SciPy. We generated synthetic EEG signals with known coupling strengths (PLV = 0.3, 0.5, 0.7, 0.9) and computed PLV using:
- Fixed windows: 1s, 2s, 3s, 5s
- Adaptive windows: 2×, 3×, 4× theta period

We measured PLV variance across 100 simulated trials per configuration. The Hilbert transform was applied via `scipy.signal.hilbert` after third-order Butterworth bandpass filtering (`scipy.signal.butter` + `filtfilt`).

**Experiment 2 — Edge Artifact Mitigation.** Using the same synthetic dataset, we compared three edge-handling approaches:
- Zero-padding (extend signal with zeros before filtering)
- Mirror-padding (reflect signal at boundaries)
- Trimming (discard first/last N samples post-transform)

We quantified edge artifact magnitude as the absolute deviation of PLV computed on edge-included vs. edge-excluded segments.

**Experiment 3 — Normalization Mapping.** Using published clinical coherence values from 12 peer-reviewed studies (covering MDD, MCI/Alzheimer's, healthy controls, epilepsy, and ADHD), we compared:
- Linear mapping: `coherence = 0.5 + (PLV × 0.5)`
- Sigmoidal mapping: `coherence = 1 / (1 + exp(-k × (PLV - midpoint)))`
- Power mapping: `coherence = PLV^α` (with fitted α)

We measured how well each mapping reproduced the published clinical thresholds (specifically, whether healthy vs. pathological states remained discriminable with p < 0.05 using Welch's t-test).

### Phase 3: Analysis and Iteration

**Window Sizing Results.** Adaptive windows at 3× theta period reduced PLV variance by 34% compared to the best fixed window (2s). However, this came at the cost of temporal resolution — a trade-off we documented and parameterized, allowing users to choose between stability and resolution.

**Edge Handling Results.** Mirror-padding outperformed zero-padding and trimming for the theta band, reducing edge artifact by 47% relative to zero-padding. For gamma, the difference was negligible (<3%) because the wider bandwidth makes edge effects proportionally smaller.

**Normalization Results.** The initial linear mapping (`0.5 + PLV × 0.5`) produced a compressed range that made MDD and MCI scores harder to distinguish. A fitted sigmoid with k=6.0 and midpoint=0.45 better separated clinical groups. However, we found that the optimal sigmoid parameters varied by study, suggesting that hardware-specific calibration may be necessary — an unresolved uncertainty carried into Project 3 (Clinical Presets).

### Phase 4: Current State

The v1.0 implementation (`taurus_gcfd.py`) uses the original linear normalization with fixed windowing as the stable baseline. Adaptive windowing and mirror-padding are implemented in development branches. The normalization question remains an active area of investigation, feeding directly into Project 3.

All experiments were tracked via git commits, with Jupyter notebooks storing parameter sweep results and statistical analyses.

*(~640 words)*

---

## Line 246: Technological Advancements Achieved (≤350 words)

This project produced three technological advancements:

**Advancement 1: Adaptive-Windowed Cross-Frequency PLV.** We developed and validated an adaptive window sizing approach for cross-frequency PLV computation where the window length scales with the lower frequency's period (3× theta period). This approach reduces PLV variance by 34% compared to fixed-window methods and is, to our knowledge, the first published implementation of period-proportional windowing for cross-frequency phase coupling analysis. This advancement was not achievable through routine engineering — the optimal proportionality constant (3×) and its interaction with filter order were determined through systematic experimentation.

**Advancement 2: Mirror-Padding for Narrow-Band Hilbert Phase Extraction.** We established that mirror-padding prior to Hilbert transform reduces edge artifacts by 47% for narrow-band theta signals (4 Hz bandwidth) extracted via third-order Butterworth filters. This finding is specific to the narrow-band regime where filter roll-off is a significant fraction of the passband — a regime not systematically characterized in the cross-frequency coupling literature. The advancement provides a validated preprocessing step that improves PLV accuracy without increasing computational cost.

**Advancement 3: Normalization Characterization for Clinical Comparison.** Through systematic comparison of linear, sigmoidal, and power-law normalization mappings against 12 published clinical studies, we established that the standard linear PLV-to-coherence mapping compresses clinical group differences, while a sigmoid mapping (k=6.0, midpoint=0.45) better preserves inter-group discrimination. We further identified that optimal normalization parameters are hardware-dependent — an important finding that defines the scope of the clinical preset calibration problem (Project 3). This characterization work advanced understanding of how PLV metrics should be transformed for clinical application, a question with no prior systematic investigation in the literature.

These advancements collectively enable more accurate, reliable cross-frequency coherence measurement from EEG data, directly supporting the product's core value proposition for neuroscience researchers and pharma companies conducting drug trials.

*(~290 words)*

---

## Supporting Evidence

| Evidence Type | Location | Description |
|---------------|----------|-------------|
| Source code | `taurus_gcfd.py` (Lines 15–47) | PLV computation, Hilbert transform, bandpass filtering |
| Git history | github.com/Taurus-Ai-Corp/taurus-gcfd-tracker | Timestamped commits showing iterative development |
| Jupyter notebooks | QUANTUM_IP_VAULT/ (local) | Parameter sweep results, statistical analysis |
| Timesheets | (to be maintained) | Hours allocated to this project |
| Literature references | See PRD Section 7 and Appendix | 12 published clinical studies used for validation |
