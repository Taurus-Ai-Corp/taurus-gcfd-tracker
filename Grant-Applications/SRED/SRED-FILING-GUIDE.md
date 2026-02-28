# SR&ED Filing Guide — TAURUS AI Corp

> **Classification:** PRIVATE
> **Tax Year:** 2025–2026 (first filing)
> **Filing Method:** Proxy method
> **Recommended Approach:** DIY narratives + boutique firm for financials

---

## Table of Contents

1. [SR&ED Overview](#1-sred-overview)
2. [Five-Question Test](#2-five-question-test)
3. [Qualifying Projects](#3-qualifying-projects)
4. [Proxy Method Calculation](#4-proxy-method-calculation)
5. [2025–2026 Rates and Limits](#5-2025-2026-rates-and-limits)
6. [Filing Timeline](#6-filing-timeline)
7. [Pre-Claim Approval Option](#7-pre-claim-approval-option)
8. [Consultant vs DIY Decision](#8-consultant-vs-diy-decision)
9. [Documentation Checklist](#9-documentation-checklist)
10. [CRA Audit Triggers to Avoid](#10-cra-audit-triggers-to-avoid)
11. [Stacking with IRAP](#11-stacking-with-irap)

---

# 1. SR&ED Overview

The Scientific Research and Experimental Development (SR&ED) program is Canada's largest single source of federal support for industrial R&D. It provides tax incentives (investment tax credits) for qualifying R&D expenditures.

**Why this matters for TAURUS AI Corp:**
- We are developing novel signal processing algorithms with genuine technological uncertainty
- The PLV cross-frequency coupling implementation involves systematic investigation
- Clinical preset calibration has no guaranteed outcome
- All development is done in Canada by Canadian residents

**Key terminology:**
- **ITC** = Investment Tax Credit (the refund)
- **CCPC** = Canadian-Controlled Private Corporation (we qualify)
- **T661** = The form filed with CRA for each SR&ED project
- **Proxy method** = Simplified overhead calculation (55% of salaries)
- **PPA** = Prescribed Proxy Amount (the 55% overhead add-on)

---

# 2. Five-Question Test

CRA uses five questions to determine if work qualifies as SR&ED. Here's how our projects map:

### Question 1: Was there a scientific or technological uncertainty?

**Yes.** Three distinct uncertainties:
1. Whether PLV computation can be made accurate for cross-frequency coupling with adaptive windowing (no standard methodology exists)
2. Whether the Hilbert transform can produce valid phase estimates on streaming data with bounded latency (edge effects are unresolved in the literature)
3. Whether clinical preset parameters derived from diverse published studies (different hardware, different montages, different preprocessing) can be unified into a single parameter set that reproduces published coherence values within ±10%

### Question 2: Did the effort involve formulating hypotheses?

**Yes.** For each project:
- PLV: "An adaptive window size proportional to the lower frequency's period will produce more stable PLV estimates than fixed windows"
- Streaming: "An overlap-add approach with 75% overlap will maintain Hilbert transform accuracy within 5% of full-signal computation"
- Presets: "Published theta-gamma coherence values can be reproduced within ±10% using a hardware-agnostic parameter normalization approach"

### Question 3: Was the overall approach consistent with systematic investigation?

**Yes.** Each project follows a structured methodology:
- Literature review → hypothesis formulation → implementation → testing against known datasets → statistical validation → iteration
- All code changes tracked in git with descriptive commit messages
- Jupyter notebooks document experimental results
- Each iteration produces quantitative metrics compared against baseline

### Question 4: Did the work lead to technological advancement?

**Yes.** Advances include:
- A novel adaptive-windowed PLV algorithm that outperforms fixed-window approaches on synthetic and real EEG data
- A validated approach to streaming Hilbert transform computation for phase coupling analysis
- The first published set of cross-condition clinical presets for theta-gamma coherence measurement

### Question 5: Was a record of the hypotheses tested and results kept?

**Yes.** Documentation includes:
- Git commit history with descriptive messages (GitHub: Taurus-Ai-Corp/taurus-gcfd-tracker)
- Jupyter notebooks with experimental results and visualizations
- CI/CD test results (GitHub Actions logs)
- This filing guide and the three T661 narratives

---

# 3. Qualifying Projects

| # | Project Title | T661 Narrative | Qualifying Period |
|---|--------------|----------------|-------------------|
| 1 | Cross-Frequency PLV Algorithm Development | SRED-PROJECT-1-PLV.md | 2025–2026 |
| 2 | Real-Time Streaming Processing Pipeline | SRED-PROJECT-2-STREAMING.md | 2026 |
| 3 | Clinical Preset Parameter Calibration | SRED-PROJECT-3-PRESETS.md | 2026 |

### What Does NOT Qualify

- Marketing, sales, or business development activities
- Routine software development (UI, deployment, CI/CD setup)
- Conference attendance
- Patent filing (the legal work, not the inventive work)
- Bug fixes that don't involve technological uncertainty
- Gradio dashboard development (routine web UI)

---

# 4. Proxy Method Calculation

The proxy method allows us to claim overhead costs as 55% of qualifying salary expenditures, without itemizing each overhead cost.

### Formula

```
Qualifying Expenditure = Qualifying Salaries + (Qualifying Salaries × 0.55)
                       = Qualifying Salaries × 1.55

ITC (Enhanced Rate)    = Qualifying Expenditure × 0.35

ITC (Basic Rate)       = Qualifying Expenditure × 0.15
```

### Example Calculation (Year 1)

| Line Item | Amount | Notes |
|-----------|--------|-------|
| Founder salary allocated to SR&ED | CAD 60,000 | ~67% of time on qualifying R&D |
| Contractor salary (ML engineer) | CAD 17,000 | SR&ED portion only |
| **Total qualifying salaries** | **CAD 77,000** | |
| Prescribed Proxy Amount (55%) | CAD 42,350 | 77,000 × 0.55 |
| Materials consumed | CAD 5,000 | Datasets, cloud compute for experiments |
| **Total qualifying expenditure** | **CAD 124,350** | |
| **ITC at enhanced rate (35%)** | **CAD 43,523** | Refundable for CCPC |
| **ITC at basic rate (15%)** | **CAD 18,653** | If enhanced rate doesn't apply |

**Important:** If any of these salaries are reimbursed by IRAP, subtract those amounts first. Only the unreimbursed portion qualifies for SR&ED.

### Why Proxy Method (Not Traditional)

| Factor | Proxy Method | Traditional Method |
|--------|-------------|-------------------|
| Overhead calculation | Automatic (55% of salaries) | Must itemize every overhead cost |
| Documentation burden | Lower | Higher (need receipts for all overhead) |
| Audit risk | Lower (CRA accepts the 55%) | Higher (CRA can challenge each item) |
| Best for | Small companies with few employees | Large companies with detailed cost accounting |

**Decision: Use proxy method.** We are a small team and the simplified calculation reduces both filing complexity and audit risk.

---

# 5. 2025–2026 Rates and Limits

The December 2024 Fall Economic Statement significantly improved SR&ED for CCPCs:

| Parameter | Previous | Current (2025–2026) |
|-----------|----------|-------------------|
| Annual Expenditure Limit | CAD 3,000,000 | **CAD 6,000,000** |
| Maximum Enhanced ITC (35%) | CAD 1,050,000 | **CAD 2,100,000** |
| Phase-Out Thresholds (taxable capital) | $10M–$50M | **$15M–$75M** |
| Capital Expenditures | Excluded (since 2012) | **Reinstated as eligible** |
| Enhanced Rate | 35% (refundable) | 35% (refundable) — unchanged |
| Basic Rate | 15% (non-refundable) | 15% (non-refundable) — unchanged |

**What this means for us:**
- Our expenditures are well below the $6M limit — we get the full enhanced rate
- Our taxable capital is well below $15M — no phase-out reduction
- Capital expenditures (hardware) now qualify — can claim development hardware

---

# 6. Filing Timeline

SR&ED claims are filed with the T2 corporate income tax return.

| Event | Deadline | Notes |
|-------|----------|-------|
| Tax year end | Per corporate calendar | Confirm with accountant |
| T661 filing deadline | 18 months after tax year end | **Hard deadline — no extensions** |
| Recommended filing | With T2 return | Don't wait until the 18-month deadline |
| CRA processing time | 60 days (complete claim) to 180 days (reviewed claim) | |
| ITC refund received | 90–180 days after filing | Refundable ITCs are paid directly |

### Our Timeline

| Date | Action |
|------|--------|
| Now (Feb 2026) | Begin documenting qualifying activities (timesheets, git logs) |
| Apr 2026 | Consider pre-claim approval for 2026 projects (see Section 7) |
| Q4 2026 | Begin drafting T661 narratives (use SRED-PROJECT-*.md as templates) |
| Q1 2027 | File T661 + T2 return with qualifying 2025–2026 expenditures |
| Q2–Q3 2027 | Receive ITC refund (CAD 43K–150K depending on qualifying spend) |

---

# 7. Pre-Claim Approval Option

Starting **April 1, 2026**, CRA offers a new elective pre-claim approval process:

| Feature | Detail |
|---------|--------|
| When available | April 1, 2026 onward |
| Processing time | 90 days (target) |
| What it does | CRA confirms your project qualifies for SR&ED BEFORE you file |
| Why it helps | Eliminates audit risk; gives certainty on refund amount |
| Cost | No charge |
| Binding? | Yes — CRA is bound by the pre-approval for that claim year |

**Recommendation:** File for pre-claim approval in April 2026 for Project 1 (PLV Algorithm). This gives us certainty before committing significant expenditure to Projects 2 and 3. If approved, we know the methodology is accepted and can apply the same approach to subsequent projects.

---

# 8. Consultant vs DIY Decision

### Recommended Approach: Hybrid

| Component | Who Does It | Why |
|-----------|------------|-----|
| **T661 technical narratives** (Lines 242, 244, 246) | **Founder (DIY)** | You know the tech. No consultant can describe your algorithmic uncertainty as accurately. CRA values authentic technical descriptions. |
| **Financial calculations** (proxy method, qualifying expenditures, ITC computation) | **Boutique SR&ED firm** | They know the CRA rules, can optimize the claim, and will handle the T661 financial sections correctly. |
| **T2 corporate tax return** | **Accountant** | Standard practice — SR&ED claim is filed WITH the T2. |

### Cost Comparison

| Approach | Cost | Risk |
|----------|------|------|
| Full DIY | $0 | Higher audit risk if financials are wrong |
| Full consultant | $15K–$50K (or 15–30% of refund) | Narratives may be generic; consultant doesn't know your tech |
| **Hybrid (recommended)** | **$5K–$15K flat fee** | Best of both — authentic narratives + correct financials |

### Red Flags in SR&ED Consultants

Avoid firms that:
- Charge a percentage of the refund (creates incentive to inflate claims)
- Promise specific refund amounts before reviewing your work
- Write the technical narratives themselves without extensive founder input
- Can't explain the five-question test in plain language
- Have CRA audit failure rates they won't disclose

### What to Look For

- Flat-fee pricing ($5K–$15K for a company our size)
- Experience with software/algorithm companies (not just manufacturing)
- References from similar-sized tech startups
- Willingness to review founder-written narratives and improve them
- Located in Canada (understands regional CRA office patterns)

---

# 9. Documentation Checklist

CRA can request contemporaneous documentation at any time. Build this as you go — NOT retroactively.

### Must Have (Start Now)

- [ ] **Timesheets** — Track hours spent on each SR&ED project vs. non-qualifying work. Use a simple spreadsheet with: Date, Project, Hours, Description of work.
- [ ] **Git commit history** — Already exists. Ensure commit messages describe WHAT was tried and WHY (e.g., "Test adaptive windowing with period-proportional size — hypothesis: reduces PLV variance by >20%")
- [ ] **Jupyter notebooks** — Document experiments, parameter sweeps, and results. Include both successful and failed experiments.
- [ ] **Meeting notes** — If discussing technical approaches with contractors or advisors, save notes.
- [ ] **Literature references** — Save PDFs or URLs of papers referenced during R&D.

### Nice to Have

- [ ] **Technical blog posts** — Publishing about your methodology creates timestamped evidence
- [ ] **Conference abstracts/posters** — If submitted, these prove the work was happening
- [ ] **Code review comments** — GitHub PR reviews documenting technical decisions
- [ ] **Slack/email threads** — Technical discussions with collaborators

### What CRA Actually Looks At

In an audit, CRA will request:
1. T661 form (your narratives + financials)
2. Timesheets showing allocation of hours
3. Source code changes (git log) during the claimed period
4. Evidence of systematic investigation (experiments, parameter sweeps)
5. Evidence that uncertainty existed (show what you didn't know at the start)

**Critical:** CRA expects documentation that was created DURING the work, not written after-the-fact for the claim. Start your timesheets NOW.

---

# 10. CRA Audit Triggers to Avoid

SR&ED claims are selected for review based on risk indicators. Minimize these:

| Trigger | Why It Flags | How to Avoid |
|---------|-------------|-------------|
| **Claim is disproportionate to revenue** | A $200K claim on $10K revenue looks suspicious | Our claim will be modest (~$43K–$150K) relative to our expenditure base |
| **Narratives are generic/boilerplate** | Signals consultant-written, not authentic R&D | Write narratives yourself using specific technical language |
| **No contemporaneous documentation** | Suggests claim is retroactive fabrication | Start timesheets and experiment logs NOW |
| **100% of salary claimed as SR&ED** | Nobody does R&D 100% of the time | Claim 60–70% of founder salary (realistic for our work split) |
| **Claiming routine development as R&D** | UI work, deployment, bug fixes don't qualify | Be honest about what's R&D vs. routine |
| **First-time filer** | CRA reviews a higher % of first claims | Use a boutique firm for financials to ensure proper filing |
| **Large contractor payments to related parties** | CRA scrutinizes non-arm's length payments | Ensure contractor is truly arm's length with market-rate compensation |

### Safe Claim Profile

| Factor | Our Approach | Risk Level |
|--------|-------------|------------|
| Claim size | CAD 43K–150K | Low (modest) |
| Salary allocation | 67% of founder time | Low (reasonable) |
| Documentation | Git logs + Jupyter notebooks + timesheets | Low (strong) |
| Narratives | Founder-written, technically specific | Low |
| Filing method | With T2, prepared by accountant + SR&ED firm | Low |
| First-time filer | Yes | Medium (mitigated by professional preparation) |

---

# 11. Stacking with IRAP

### Rule

The same dollar of expenditure **cannot** be claimed under both IRAP reimbursement and SR&ED ITC. However, different expenditures from the same company in the same period CAN be split across programs.

### Our Stacking Strategy

```
┌──────────────────────────────────────────────────────┐
│ Total R&D Expenditure                                 │
│                                                       │
│  ┌────────────────────┐  ┌─────────────────────────┐ │
│  │ IRAP-funded work   │  │ Non-IRAP work           │ │
│  │                    │  │                          │ │
│  │ Lead dev salary    │  │ R&D done before IRAP     │ │
│  │ (80% reimbursed)   │  │ Founder time on non-IRAP │ │
│  │                    │  │ projects                 │ │
│  │ Contractor salary  │  │ Overhead (proxy method)  │ │
│  │ (50% reimbursed)   │  │ Materials consumed       │ │
│  │                    │  │                          │ │
│  │ ❌ NOT SR&ED       │  │ ✅ QUALIFIES for SR&ED  │ │
│  │ eligible           │  │                          │ │
│  └────────────────────┘  └─────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

### Practical Example

| Expenditure | Total | IRAP Covers | Company Pays | SR&ED Eligible? |
|------------|-------|-------------|--------------|-----------------|
| Lead dev salary (IRAP project) | $90,000 | $72,000 | $18,000 | **$18,000** (company portion only) |
| Contractor (IRAP project) | $17,000 | $8,500 | $8,500 | **$8,500** (company portion only) |
| Lead dev salary (non-IRAP R&D) | $30,000 | $0 | $30,000 | **$30,000** (fully eligible) |
| Materials | $5,000 | $0 | $5,000 | **$5,000** (fully eligible) |
| **Total SR&ED qualifying** | — | — | — | **$61,500** |
| PPA (55% of qualifying salaries) | — | — | — | **$31,075** |
| **Total SR&ED expenditure** | — | — | — | **$92,575** |
| **ITC at 35%** | — | — | — | **$32,401** |

**Result:** We get CAD 80,500 from IRAP + CAD 32,401 from SR&ED = **CAD 112,901 total non-dilutive funding** on a project that costs us $152,500 total. Our effective out-of-pocket: ~CAD 39,600.

---

## Next Steps

1. **Now:** Start timesheets tracking SR&ED-qualifying hours
2. **Now:** Ensure git commits describe experimental methodology
3. **Mar 2026:** Contact boutique SR&ED firm (get 3 quotes, flat-fee only)
4. **Apr 2026:** File pre-claim approval for Project 1 (PLV)
5. **Oct 2026:** Draft T661 narratives using SRED-PROJECT-*.md templates
6. **Q1 2027:** File T661 with T2 return
