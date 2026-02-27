# taurus-gcfd-tracker

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![HuggingFace Space](https://img.shields.io/badge/%F0%9F%A4%97%20HF%20Space-Live%20Demo-yellow)](https://huggingface.co/spaces/Taurus-Ai-Corp/gcfd-coherence-tracker)
[![CI](https://github.com/Taurus-Ai-Corp/taurus-gcfd-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/Taurus-Ai-Corp/taurus-gcfd-tracker/actions)

**Generalized Cross-Frequency Decomposition (GCFD) for EEG/MEG phase synchronization.**

Quantifies theta-gamma coupling using Phase Locking Value (PLV) to measure global neural coherence. Built by [TAURUS AI Corp](https://taurusai.io) as part of the Global Bio-Foundry initiative.

[Live Demo](https://huggingface.co/spaces/Taurus-Ai-Corp/gcfd-coherence-tracker) | [Enterprise Licensing](#enterprise--commercial-use) | [Citation](#citation)

---

## Overview

`taurus-gcfd-tracker` implements the **Global Coherence Field Decomposition** algorithm, which measures the consistency of phase relationships between theta (4-8 Hz) and gamma (30-100 Hz) oscillations in EEG/MEG recordings.

**Method:**

```
Raw EEG -> Butterworth bandpass (order 3, zero-phase) -> Hilbert transform
        -> Phase extraction -> Phase Locking Value -> Sliding window analysis
        -> Global Coherence Score [0.5 - 1.0]
```

**Clinical interpretation:**

| Score | Status | Meaning |
|-------|--------|---------|
| 0.90+ | HEALTHY | Strong theta-gamma coupling |
| 0.70-0.89 | MODERATE | Partial synchronization |
| < 0.70 | LOW | Weak coupling / potential pathology |

> Scores above 0.95 may indicate pathological hypersynchronization (e.g., epileptic ictal states).

## Installation

```bash
pip install numpy scipy matplotlib
git clone https://github.com/Taurus-Ai-Corp/taurus-gcfd-tracker.git
cd taurus-gcfd-tracker
```

## Quick Start

```python
from taurus_gcfd import CoherenceTracker, datasets

# Load simulated EEG data
data = datasets.load_sample_eeg('patient_01_mdd')

# Initialize tracker
tracker = CoherenceTracker(sampling_rate=250)

# Calculate Global Coherence Ratio
score = tracker.calculate_global_coherence(data)
print(f"Global Coherence: {score:.3f}")

# Plot spatio-spectral eigenmodes
tracker.plot_eigenmodes(data, target_frequency='theta_gamma')
```

## Live Demo

Try the interactive Gradio app with 8 clinical presets:

[Launch on HuggingFace Spaces](https://huggingface.co/spaces/Taurus-Ai-Corp/gcfd-coherence-tracker)

**Presets:** Healthy Adult, MDD, MCI/Alzheimer's, Epilepsy, Meditation, Anesthesia, ADHD, Custom

**API Access:**

```python
from gradio_client import Client

client = Client("Taurus-Ai-Corp/gcfd-coherence-tracker")
result = client.predict(
    preset="Major Depressive Disorder (MDD)",
    duration=10, fs=250,
    theta_amp=0.5, gamma_amp=0.3, noise_level=2.0, seed=101,
    theta_low=4.0, theta_high=8.0, gamma_low=30.0, gamma_high=100.0,
    csv_file=None,
    api_name="/run_analysis"
)
```

## API Reference

### `CoherenceTracker(sampling_rate=250)`

| Method | Returns | Description |
|--------|---------|-------------|
| `calculate_global_coherence(eeg_data, band1=(4,8), band2=(30,100))` | float [0-1] | PLV-based coherence score |
| `plot_eigenmodes(data, target_frequency)` | matplotlib figure | Frequency-domain visualization |

### `datasets.load_sample_eeg(patient_id)` -> np.ndarray

Generates synthetic EEG data (2500 samples at 250 Hz) for testing.

## Community Validation

We invite the neuro-tech and neuroscience communities to test this tool against clinical datasets to independently verify theta-gamma phase synchronization patterns using the PLV methodology.

## Enterprise & Commercial Use

This library is **Apache 2.0** for individual, academic, and research use.

**Enterprise License** is required for:
- Clinical software products (FDA/CE-marked devices)
- SaaS platforms redistributing this tracker as a service
- Integration into proprietary neurotechnology pipelines
- Government contracts and defense applications

**API Tiers:**

| Tier | Rate | Price |
|------|------|-------|
| Free | 50 req/day | $0 |
| Researcher | 1,000 req/day | $29/mo |
| Clinical | 10,000 req/day + batch | $149/mo |
| Enterprise | Unlimited + SLA | Contact us |

Contact: [admin@taurusai.io](mailto:admin@taurusai.io)
See [LICENSE-ENTERPRISE](LICENSE-ENTERPRISE) for terms.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). We welcome:
- Additional frequency band presets
- Dataset integrations (EEGLAB, MNE-Python)
- Performance optimizations
- Clinical validation case studies

## Citation

```bibtex
@software{taurus_gcfd_2026,
  author       = {TAURUS AI Corp},
  title        = {taurus-gcfd-tracker: Generalized Cross-Frequency Decomposition for EEG/MEG Coherence},
  year         = 2026,
  version      = {1.0.0},
  publisher    = {GitHub},
  url          = {https://github.com/Taurus-Ai-Corp/taurus-gcfd-tracker}
}
```

## Strategy & Business

- [Product Requirements Document (PRD)](docs/PRD.md) -- comprehensive product, market, and business strategy
- [Why Big Companies Can't Move Fast](WHY-BIG-COMPANIES-CANT-MOVE-FAST.md) -- our structural advantages

## References

1. Lachaux et al. (1999) -- *Measuring phase synchrony in brain signals*
2. Canolty et al. (2006) -- *High gamma power is phase-locked to theta oscillations*
3. Tort et al. (2010) -- *Measuring phase-amplitude coupling between neuronal oscillations*

## License

Apache License 2.0 -- see [LICENSE](LICENSE).
Commercial use requires an Enterprise License -- see [LICENSE-ENTERPRISE](LICENSE-ENTERPRISE).

---

*Maintained by [TAURUS AI Corp](https://taurusai.io) -- pioneering quantum-safe biological signal analysis.*
