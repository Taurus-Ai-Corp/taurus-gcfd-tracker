---
title: 'taurus-gcfd-tracker: An Open-Source Tool for Theta-Gamma Phase Synchronization Analysis'
tags:
  - Python
  - neuroscience
  - EEG
  - phase synchronization
  - cross-frequency coupling
  - PLV
  - theta-gamma
authors:
  - name: TAURUS AI Corp
    affiliation: 1
    # TODO: Replace with individual author name and ORCID before JOSS submission
    # - given-names: [First]
    #   surname: [Last]
    #   orcid: 0000-0000-0000-0000
affiliations:
  - name: TAURUS AI Corp, Canada
    index: 1
date: 27 February 2026
bibliography: paper.bib
---

# Summary

`taurus-gcfd-tracker` is a Python library for computing cross-frequency phase synchronization from electroencephalography (EEG) and magnetoencephalography (MEG) signals. The library calculates the Phase Locking Value (PLV) between theta (4–8 Hz) and gamma (30–100 Hz) oscillations — a biomarker whose strength correlates with neurological health and whose disruption is observed in depression, Alzheimer's disease, epilepsy, and ADHD. The tool provides a complete pipeline from raw signal to coherence score: Butterworth bandpass filtering, Hilbert-transform-based phase extraction, PLV computation, and clinical classification. It ships with eight condition-specific parameter presets, a synthetic EEG generator with genuine phase-amplitude coupling, sliding-window temporal analysis, and an interactive web dashboard hosted on HuggingFace Spaces. The library is free and open-source (Apache 2.0), requires only `numpy`, `scipy`, and `matplotlib`, and is designed to eliminate the need for researchers to write hundreds of lines of custom phase coupling code per study.

# Statement of Need

Cross-frequency coupling (CFC) between theta and gamma oscillations is a well-established biomarker for cognitive function and neurological health [@canolty2006; @canolty2010]. Strong theta-gamma phase locking indicates healthy cross-frequency communication, while weak coupling correlates with major depressive disorder [@sun2022], mild cognitive impairment and Alzheimer's disease [@goodman2018], ADHD [@kim2015], and altered states of consciousness [@lutz2004]. Quantifying this coupling is central to clinical neuroscience research, particularly in pharmaceutical trials measuring treatment response via EEG biomarkers.

Despite the importance of CFC analysis, researchers face significant tooling barriers. The dominant EEG toolbox, EEGLAB [@delorme2004], requires MATLAB — a commercial license costing USD 860 or more per year. MNE-Python [@gramfort2013], the leading open-source alternative with over 33,000 weekly PyPI downloads, provides general-purpose signal processing but does not include a built-in cross-frequency PLV function. Researchers must implement their own phase coupling analysis — typically 200 to 500 lines of custom code per study — introducing variability across labs and wasting PhD-level engineering time. NeuroKit2 [@makowski2021] offers a PLV implementation but lacks clinical reference presets, sliding-window analysis, and a hosted interface for non-programmers.

Commercial platforms exist (e.g., Beacon Biosignals, which raised USD 121 million as of November 2025) but are closed-source, opaque in pricing, and inaccessible to individual researchers. `taurus-gcfd-tracker` fills this gap: it is free for researchers, provides condition-specific presets that no other tool offers, and includes an interactive web interface requiring zero installation.

# State of the Field

| Tool | Language | PLV CFC | Clinical Presets | Hosted UI | License |
|------|----------|---------|-----------------|-----------|---------|
| MNE-Python [@gramfort2013] | Python | No | No | No | BSD-3 |
| EEGLAB [@delorme2004] | MATLAB | Via plugins | No | No | GPL-2 (requires MATLAB) |
| NeuroKit2 [@makowski2021] | Python | Basic | No | No | MIT |
| BrainVision Analyzer | Proprietary | Yes | Limited | No | Commercial ($3K–$12K) |
| Beacon Biosignals | Proprietary | Yes | Yes | Yes | Enterprise-only |
| **taurus-gcfd-tracker** | **Python** | **Yes** | **8 conditions** | **HuggingFace** | **Apache 2.0** |

Our primary differentiation is the combination of open-source accessibility with clinical presets — validated parameter sets for Healthy, MDD, MCI/Alzheimer's, Epilepsy, Meditation, Anesthesia, ADHD, and Custom configurations. Each preset specifies signal generation parameters calibrated against published literature values, enabling reproducible benchmarking across studies.

# Software Design

The analysis pipeline implements the Phase Locking Value metric originally defined by @lachaux1999. The architecture consists of four sequential stages:

1. **Bandpass filtering**: Third-order zero-phase Butterworth filters (`scipy.signal.butter` + `filtfilt`) isolate theta and gamma frequency bands. Zero-phase filtering via `filtfilt` avoids the phase distortion that would invalidate PLV computation [@virtanen2020]. The filter order of 3 balances frequency selectivity against temporal ringing — critical for preserving the phase relationships being measured.

2. **Phase extraction**: The Hilbert transform (`scipy.signal.hilbert`) converts each bandpass-filtered signal to its analytic representation, from which instantaneous phase is extracted via `numpy.angle` [@harris2020]. This yields continuous phase time series for both frequency bands.

3. **PLV computation**: The Phase Locking Value is calculated as $PLV = \left| \frac{1}{N} \sum_{t=1}^{N} e^{i(\phi_1(t) - \phi_2(t))} \right|$, where $\phi_1$ and $\phi_2$ are the instantaneous phases of the theta and gamma bands respectively. PLV ranges from 0 (no phase coupling) to 1 (perfect phase locking). The global coherence score is derived as $\text{score} = 0.5 + 0.5 \times PLV$, mapping to a [0.5, 1.0] range where clinical thresholds are applied: scores above 0.90 indicate healthy coupling, 0.70–0.89 moderate coupling, and below 0.70 disrupted coupling consistent with pathological states.

4. **Temporal analysis**: Sliding-window PLV computation (2-second windows, 0.5-second steps) captures the temporal dynamics of phase coupling, enabling detection of transient synchronization events and assessment of coupling stability over time.

The synthetic EEG generator models physiologically grounded signals: theta oscillations (5.5 Hz $\pm$ 0.5 Hz), gamma oscillations (38 Hz $\pm$ 3 Hz) with genuine phase-amplitude coupling (gamma envelope modulated by theta phase as $1 + 0.5\cos(\phi_\theta)$), alpha background activity (10 Hz), 1/f pink noise, and 60 Hz line noise. This composition enables meaningful method validation without requiring clinical data access.

# Research Impact Statement

`taurus-gcfd-tracker` is publicly available on GitHub under the Apache 2.0 license, with an interactive web interface hosted on HuggingFace Spaces. Continuous integration validates code correctness via automated tests on every commit. Synthetic EEG datasets for all seven clinical conditions are published on HuggingFace Hub as `Taurus-Ai-Corp/gcfd-synthetic-eeg`, tagged for discoverability by the neuroscience community. The library is used in TAURUS AI Corp's quantum biology research program investigating room-temperature coherence in biological systems.

# AI Usage Disclosure

Claude Code (Anthropic) assisted with automated test generation, documentation formatting, and CI/CD configuration. All scientific content — algorithm design, clinical preset parameters, and research claims — was authored by human researchers. The core signal processing pipeline was written entirely by human developers.

# References
