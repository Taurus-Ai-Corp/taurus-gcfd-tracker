# IRAP Project Proposal — GCFD Coherence Tracker

> **Applicant:** TAURUS AI Corp
> **Project Title:** Advanced EEG Phase Synchronization Library for Neuroscience Research and Clinical Trials
> **Requested Contribution:** CAD 80,500
> **Project Duration:** 10 months
> **Date:** February 2026
> **Classification:** PRIVATE — for ITA review only

---

## Table of Contents

1. [Company Overview](#1-company-overview)
2. [Project Description](#2-project-description)
3. [Technical Objectives](#3-technical-objectives)
4. [Work Plan & Milestones](#4-work-plan--milestones)
5. [Budget](#5-budget)
6. [Benefits to Canada](#6-benefits-to-canada)

---

# 1. Company Overview

## 1.1 Company Information

| Field | Detail |
|-------|--------|
| Legal Name | TAURUS AI Corp |
| Incorporation | Canadian corporation |
| Location | Canada |
| Employees | 1 (founder) + contractors |
| Founded | 2024 |
| Website | taurusai.io |
| Sector | HealthTech / Neurotechnology / Scientific Software |

## 1.2 Company Description

TAURUS AI Corp develops quantum-safe software infrastructure and neurotechnology tools. The company's core competency is bridging advanced signal processing research with production-grade open-source software.

Our flagship product, **taurus-gcfd-tracker**, is an open-source Python library for measuring brain wave synchronization — specifically, cross-frequency phase coupling between theta (4–8 Hz) and gamma (30–100 Hz) oscillations in EEG and MEG signals. This coupling is a validated biomarker for neurological health: strong coupling indicates healthy brain coordination, while weak coupling correlates with major depressive disorder (MDD), mild cognitive impairment (MCI/Alzheimer's), ADHD, and other conditions.

The library is currently live on:
- **GitHub:** github.com/Taurus-Ai-Corp/taurus-gcfd-tracker (Apache 2.0 open-source)
- **HuggingFace Spaces:** Interactive web dashboard for researchers
- **CI/CD pipeline:** Automated testing, linting, and IP protection scanning

## 1.3 Team

| Role | Expertise | Commitment |
|------|-----------|------------|
| Founder / Lead Developer | Full-stack software engineering, signal processing, post-quantum cryptography, AI/ML pipeline architecture | Full-time |
| ML Engineer (contractor) | GPU-accelerated computing, batch processing, performance optimization | Part-time (planned) |
| Mitacs Intern (planned) | EEG signal processing, neuroscience domain expertise | Q3 2026 (pending) |

## 1.4 Product Status

| Component | Status | Evidence |
|-----------|--------|----------|
| Core algorithm (PLV-based coherence) | Production v1.0 | GitHub: taurus_gcfd.py |
| 8 clinical presets | Implemented | Healthy, MDD, MCI, Epilepsy, Meditation, Anesthesia, ADHD, Custom |
| Gradio web dashboard | Live | HuggingFace Space |
| API access | Live | Via gradio_client |
| CI/CD (lint + test + IP guard) | Passing | GitHub Actions |
| PyPI package | Not yet released | Planned for v2.0 |

---

# 2. Project Description

## 2.1 Problem Statement

Three billion people worldwide have neurological disorders (WHO, 2021). Researchers studying these conditions need to measure brain wave synchronization from EEG recordings. The current tools are inadequate:

**Problem 1: MATLAB Lock-In**
The dominant EEG toolbox, EEGLAB (20,464 citations), requires MATLAB — a $860+/year commercial license. New researchers learn Python, not MATLAB. The field is migrating, but Python alternatives lack specialized cross-frequency analysis.

**Problem 2: No Turnkey PLV Solution**
MNE-Python (33,000 weekly PyPI downloads) provides raw signal processing building blocks but **no built-in Phase Locking Value (PLV) computation for cross-frequency coupling**. Researchers must write 200–500 lines of custom code to replicate what should be a single function call. This creates inconsistency across studies and wastes PhD-level engineering time.

**Problem 3: No Clinical Presets**
Pharma companies running drug trials need condition-specific analysis parameters (filter bands, window sizes, thresholds) for MDD, Alzheimer's, epilepsy, etc. No existing tool ships these presets. Each trial reinvents them, introducing variability and reducing reproducibility.

**Problem 4: No Real-Time Capability**
Neurofeedback applications and brain-computer interfaces need streaming coherence analysis. Current tools operate in batch mode only. Building a real-time pipeline requires expertise in both signal processing and systems engineering that few labs possess.

## 2.2 Proposed Solution

We will advance **taurus-gcfd-tracker** from a working v1.0 prototype to a production-grade v2.0 library with five key innovations:

1. **PyPI-installable package** — `pip install taurus-gcfd` makes the tool accessible to 33,000+ MNE-Python users without any manual setup
2. **MNE-Python plugin** — Native integration with the dominant Python EEG framework via `mne.io` loader compatibility
3. **Multi-channel processing** — Scale from single-channel to 64-channel EEG montages (current limitation: single-channel only)
4. **Streaming API** — WebSocket-based real-time coherence computation for neurofeedback and BCI applications
5. **Clinical benchmark suite** — Validated presets benchmarked against published literature values for 8 neurological conditions

## 2.3 Why Existing Solutions Don't Solve This

| Tool | What It Does | What It Doesn't Do |
|------|-------------|-------------------|
| **MNE-Python** | General EEG signal processing | No built-in PLV cross-frequency coupling; no clinical presets |
| **EEGLAB** | Comprehensive EEG toolbox | Requires MATLAB ($860+/yr); no Python API; no streaming |
| **Beacon Biosignals** | Enterprise EEG platform for pharma | Proprietary, opaque pricing; no open-source component; no researcher access |
| **BrainVision Analyzer** | Clinical EEG analysis | $3K–$12K/seat; Windows-only; no programmable API |
| **NeuroKit2** | Python physiological signal toolkit | Broad scope (ECG, EMG, EEG); PLV implementation is basic; no clinical presets |

Our innovation sits in the gap: **free for researchers, production-grade for enterprise, with clinical presets that don't exist anywhere else.**

## 2.4 Market Opportunity

| Metric | Value | Source |
|--------|-------|--------|
| EEG analysis software market (2024) | USD 605M | Business Research Insights |
| Projected (2033) | USD 1.19B (7.8% CAGR) | Business Research Insights |
| Serviceable addressable market | ~USD 120M | Phase coupling segment |
| Key competitor validation | Beacon Biosignals: $121M raised ($86M Series B, Nov 2025) | Crunchbase |
| CNS biomarker market | USD 4.81B (2024) → USD 8.73B (2030) | Credence Research |

---

# 3. Technical Objectives

## 3.1 Deliverables

| # | Deliverable | Success Criteria | Timeline |
|---|------------|-----------------|----------|
| 1 | **PyPI Package v2.0** | Published on PyPI; installable via `pip install taurus-gcfd`; passes all unit tests; documentation on ReadTheDocs | Month 1–2 |
| 2 | **MNE-Python Plugin** | Compatible with `mne.io.read_raw_*` loaders; processes standard MNE Epochs and Evoked objects; listed in MNE ecosystem | Month 3–4 |
| 3 | **Multi-Channel Processing** | Supports 64-channel EEG montages; channel-pair coherence matrix; topographic coherence map visualization | Month 3–4 |
| 4 | **Streaming API** | WebSocket-based real-time coherence computation; latency < 100ms per window; handles OpenBCI and Muse data formats | Month 5–6 |
| 5 | **Clinical Benchmark Suite** | 8 presets benchmarked against published values (±10% of literature); benchmark report with statistical analysis; performance comparison vs MNE and EEGLAB | Month 7–10 |

## 3.2 Technical Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| PLV accuracy diverges from literature values on real clinical data | Medium | High | Use public PhysioNet datasets with known coherence profiles; statistical validation against EEGLAB reference implementation |
| Multi-channel processing exceeds memory limits on standard hardware | Low | Medium | Implement chunked processing; leverage NumPy memory-mapped arrays; benchmark on 8GB RAM baseline |
| WebSocket streaming introduces unacceptable latency (>100ms) | Medium | Medium | Profile bottleneck (Hilbert transform vs. FFT approach); implement C extension for inner loop if needed |
| MNE-Python API changes break plugin compatibility | Low | Low | Pin MNE version; implement adapter pattern; monitor MNE release notes |

## 3.3 Innovation

The core algorithmic innovation is in **three areas of technological uncertainty** (detailed in SR&ED narratives):

1. **Cross-frequency PLV computation with adaptive windowing** — Existing PLV implementations use fixed windows. We are developing an adaptive windowing approach that adjusts to signal characteristics, which has no established methodology in the literature.

2. **Real-time streaming with overlapping Hilbert transform** — The Hilbert transform requires the full signal to compute accurately. Computing it on streaming data with bounded latency involves novel approaches to edge handling and overlap-add that have not been validated for phase coupling analysis.

3. **Clinical preset calibration** — Mapping published clinical thresholds (from studies using different hardware, montages, and preprocessing) to a single unified parameter set is a systematic investigation with no guaranteed outcome.

---

# 4. Work Plan & Milestones

## Phase 1: PyPI Package + Core API (Months 1–2)

**Objective:** Transform the existing single-file prototype into a proper Python package with public API, test suite, and documentation.

| Task | Duration | Resource |
|------|----------|----------|
| Package structure (src layout, pyproject.toml, setup) | 1 week | Lead Developer |
| Public API design (CoherenceTracker, Presets, Datasets) | 1 week | Lead Developer |
| Unit test suite (>90% coverage) | 2 weeks | Lead Developer |
| Documentation (ReadTheDocs, examples, tutorials) | 1 week | Lead Developer |
| PyPI publishing pipeline (CI/CD) | 1 week | Lead Developer |
| Alpha testing with 3 external researchers | 2 weeks | Lead Developer |

**Milestone:** `taurus-gcfd` v2.0.0 live on PyPI with passing tests and documentation.

**Cost:** CAD 19,500 (Labour: $18,000 + Cloud: $1,500)

## Phase 2: MNE Plugin + Multi-Channel (Months 3–4)

**Objective:** Integrate with the MNE-Python ecosystem and scale from single-channel to 64-channel processing.

| Task | Duration | Resource |
|------|----------|----------|
| MNE Raw/Epochs/Evoked adapter layer | 2 weeks | Lead Developer |
| Multi-channel coherence matrix computation | 2 weeks | Lead Developer + Contractor |
| Topographic coherence map visualization | 1 week | Lead Developer |
| Performance optimization (vectorized NumPy operations) | 2 weeks | Contractor |
| Integration tests with MNE sample datasets | 1 week | Lead Developer |

**Milestone:** MNE plugin installable via `pip install taurus-gcfd[mne]`; processes 64-channel data in < 30 seconds.

**Cost:** CAD 25,000 (Labour: $18,000 + Contractor: $5,000 + Cloud: $2,000)

## Phase 3: Streaming API (Months 5–6)

**Objective:** Implement real-time WebSocket streaming for neurofeedback and BCI applications.

| Task | Duration | Resource |
|------|----------|----------|
| Streaming architecture design (overlap-add Hilbert) | 2 weeks | Lead Developer |
| WebSocket server implementation | 2 weeks | Lead Developer |
| Hardware integration (OpenBCI, Muse protocols) | 2 weeks | Lead Developer + Contractor |
| Latency benchmarking and optimization | 1 week | Contractor |
| Real-time dashboard (Gradio or web) | 1 week | Lead Developer |

**Milestone:** Streaming API demo with < 100ms latency; tested with OpenBCI Cyton board.

**Cost:** CAD 26,000 (Labour: $18,000 + Contractor: $5,000 + Cloud: $3,000)

## Phase 4: Clinical Presets + Benchmarks (Months 7–8)

**Objective:** Validate and calibrate clinical presets against published literature; produce benchmark report.

| Task | Duration | Resource |
|------|----------|----------|
| Literature review: published coherence values per condition | 2 weeks | Lead Developer |
| Dataset acquisition (PhysioNet, TDBRAIN, MPI-Leipzig) | 1 week | Lead Developer |
| Preset calibration: run pipeline on clinical datasets | 2 weeks | Lead Developer + Contractor |
| Statistical validation (±10% of literature values) | 1 week | Contractor |
| Benchmark report: taurus-gcfd vs MNE vs EEGLAB | 2 weeks | Lead Developer |

**Milestone:** Published benchmark report; 8 presets validated; performance parity or better vs. EEGLAB.

**Cost:** CAD 29,000 (Labour: $18,000 + Contractor: $7,000 + Datasets/Cloud: $4,000)

## Phase 5: Integration Testing + Launch (Months 9–10)

**Objective:** End-to-end integration testing, documentation finalization, community launch.

| Task | Duration | Resource |
|------|----------|----------|
| End-to-end integration tests (all modules) | 2 weeks | Lead Developer |
| Documentation update (full API reference, tutorials) | 2 weeks | Lead Developer |
| Community launch (blog post, HuggingFace demo update, Reddit/Twitter) | 1 week | Lead Developer |
| Conference preparation (SfN 2026 poster/abstract) | 1 week | Lead Developer |
| Enterprise pilot outreach (3 pharma contacts) | 2 weeks | Lead Developer |

**Milestone:** v2.0 stable release; first enterprise pilot conversation initiated.

**Cost:** CAD 21,000 (Labour: $18,000 + Marketing/Cloud: $3,000)

---

# 5. Budget

See detailed budget in `IRAP-BUDGET.md`. Summary:

| Category | Total Cost | IRAP Contribution | Company Share |
|----------|-----------|-------------------|---------------|
| Internal Technical Labour | CAD 90,000 | CAD 72,000 (80%) | CAD 18,000 |
| Contractor Labour | CAD 17,000 | CAD 8,500 (50%) | CAD 8,500 |
| Materials, Cloud, Other | CAD 33,500 | CAD 0 | CAD 33,500 |
| Contingency (10%) | CAD 12,000 | CAD 0 | CAD 12,000 |
| **TOTAL** | **CAD 152,500** | **CAD 80,500 (53%)** | **CAD 72,000 (47%)** |

### Company's Ability to Fund Its Share

| Source | Amount |
|--------|--------|
| Operating revenue (consulting + API subscriptions) | CAD 30,000 |
| Founder salary deferral | CAD 20,000 |
| Seed investment (in progress) | CAD 22,000 |
| **Total available** | **CAD 72,000** |

---

# 6. Benefits to Canada

## 6.1 Jobs Created

| Role | When | Type | Salary |
|------|------|------|--------|
| ML Engineer (contractor → full-time) | Month 1 | Contract → FTE | CAD 85K/yr |
| Mitacs Research Intern | Month 4 | Internship (4–6 months) | CAD 15K (Mitacs) |
| Junior Developer (post-project) | Month 12 | FTE | CAD 65K/yr |
| **Total new positions by Month 12** | — | **3** | — |

## 6.2 IP Retention in Canada

All intellectual property developed under this project will remain in Canada:

- **Open-source core:** Apache 2.0 license ensures global access while maintaining Canadian origin and stewardship
- **Proprietary algorithms:** Enterprise-licensed components (clinical presets, streaming optimizations) owned by TAURUS AI Corp (Canadian corporation)
- **Patent filings:** Provisional patent for PLV algorithm innovations to be filed through Canadian IP office
- **Data sovereignty:** All user analytics and enterprise data processed on Canadian or Canadian-contracted infrastructure

## 6.3 Export Revenue Potential

| Market | Revenue Target (Year 2) | Rationale |
|--------|------------------------|-----------|
| US pharma companies | USD 100K–300K | 60% of global CNS drug trials are US-based |
| European research institutions | USD 30K–80K | Strong EEG research tradition (Germany, Netherlands, UK) |
| Asia-Pacific neurotech startups | USD 20K–50K | Fastest-growing regional market (15.46% CAGR) |

**Total export revenue potential:** USD 150K–430K (Year 2), generating Canadian tax revenue and positive trade balance.

## 6.4 Graduate Hiring (YEP Alignment)

TAURUS AI Corp commits to:
- Hiring at least **one Canadian graduate** (under 30) within 12 months of project completion
- Providing mentorship through the project's Mitacs internship component
- Targeting graduates from Canadian universities with neuroscience or computer science programs

This aligns with NRC's Youth Employment Program (YEP) mandate to create high-quality technical jobs for young Canadians.

## 6.5 Broader Impact

- **Scientific reproducibility:** Open-source tool enables consistent, reproducible brain wave analysis across labs worldwide — Canadian-origin contribution to global science
- **Healthcare innovation:** Faster, cheaper biomarker analysis accelerates drug development timelines for neurological disorders affecting 3B+ people
- **Canadian leadership in neurotechnology:** Positions Canada alongside the US (Beacon Biosignals, $121M funded) in the growing neurotech sector
- **Open-source ecosystem contribution:** Follows in the tradition of Canadian open-source projects (Shopify/Liquid, Automattic/WordPress contributors) that punch above their weight globally

---

## Appendix: Supporting Links

| Resource | URL |
|----------|-----|
| GitHub Repository | github.com/Taurus-Ai-Corp/taurus-gcfd-tracker |
| Live Demo (HuggingFace) | huggingface.co/spaces/Taurus-Ai-Corp/gcfd-coherence-tracker |
| Product Requirements Document | (Available on request — PRIVATE) |
| Competitor Reference: Beacon Biosignals | beaconbiosignals.com |
| MNE-Python (integration target) | mne.tools |
| EEGLAB (MATLAB competitor) | eeglab.org |
| WHO Neurological Disorders Report | who.int/news-room/fact-sheets/detail/neurological-disorders |
