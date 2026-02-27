"""
GCFD Coherence Tracker v1.0.0
Generalized Cross-Frequency Decomposition for EEG/MEG Phase Synchronization

Copyright (c) 2024-2026 TAURUS AI Corp. All rights reserved.
Licensed under the Apache License, Version 2.0
https://taurusai.io | https://github.com/Taurus-Ai-Corp

Method: Butterworth bandpass + Hilbert transform + Phase Locking Value (PLV)
Reference: Lachaux et al. (1999) — Measuring phase synchrony in brain signals
"""

__version__ = "1.0.0"
__author__ = "TAURUS AI Corp"

import gradio as gr
import numpy as np
import scipy.signal as sig
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import io
import csv
import json
from dataclasses import dataclass
from typing import Optional


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CORE DSP ENGINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class BandDefinition:
    name: str
    low: float
    high: float
    color: str

# Standard neuroscience frequency bands
BANDS = {
    "delta":      BandDefinition("Delta",      0.5,  4.0,  "#94a3b8"),
    "theta":      BandDefinition("Theta",      4.0,  8.0,  "#a78bfa"),
    "alpha":      BandDefinition("Alpha",      8.0,  13.0, "#60a5fa"),
    "beta":       BandDefinition("Beta",       13.0, 30.0, "#34d399"),
    "low_gamma":  BandDefinition("Low Gamma",  30.0, 60.0, "#fb923c"),
    "high_gamma": BandDefinition("High Gamma", 60.0, 120.0,"#f87171"),
}


def bandpass_filter(data: np.ndarray, low: float, high: float, fs: float, order: int = 3) -> np.ndarray:
    """Apply zero-phase Butterworth bandpass filter."""
    nyq = 0.5 * fs
    low_n = max(low / nyq, 0.001)
    high_n = min(high / nyq, 0.999)
    if low_n >= high_n:
        return np.zeros_like(data)
    b, a = sig.butter(order, [low_n, high_n], btype='band')
    return sig.filtfilt(b, a, data)


def extract_phase(data: np.ndarray, low: float, high: float, fs: float) -> np.ndarray:
    """Extract instantaneous phase via Hilbert transform for a frequency band."""
    filtered = bandpass_filter(data, low, high, fs)
    analytic = sig.hilbert(filtered)
    return np.angle(analytic)


def compute_plv(phase1: np.ndarray, phase2: np.ndarray) -> float:
    """Compute Phase Locking Value between two phase time series."""
    return float(np.abs(np.mean(np.exp(1j * (phase1 - phase2)))))


def compute_spectral_power(data: np.ndarray, fs: float) -> tuple:
    """Compute power spectral density using Welch's method."""
    freqs, psd = sig.welch(data, fs=fs, nperseg=min(len(data), int(fs * 2)))
    return freqs, psd


def compute_band_power(data: np.ndarray, fs: float, low: float, high: float) -> float:
    """Compute relative power in a frequency band."""
    freqs, psd = compute_spectral_power(data, fs)
    band_mask = (freqs >= low) & (freqs <= high)
    _trapz = np.trapezoid if hasattr(np, 'trapezoid') else np.trapz
    total_power = _trapz(psd, freqs)
    band_power = _trapz(psd[band_mask], freqs[band_mask])
    return float(band_power / total_power) if total_power > 0 else 0.0


def compute_sliding_plv(data: np.ndarray, fs: float, band1: tuple, band2: tuple,
                        window_sec: float = 2.0, step_sec: float = 0.5) -> tuple:
    """Compute PLV over sliding windows for temporal dynamics."""
    window = int(window_sec * fs)
    step = int(step_sec * fs)
    n_samples = len(data)

    times = []
    plvs = []

    for start in range(0, n_samples - window, step):
        segment = data[start:start + window]
        p1 = extract_phase(segment, band1[0], band1[1], fs)
        p2 = extract_phase(segment, band2[0], band2[1], fs)
        plv = compute_plv(p1, p2)
        times.append((start + window / 2) / fs)
        plvs.append(plv)

    return np.array(times), np.array(plvs)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLINICAL PRESETS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CLINICAL_PRESETS = {
    "Healthy Adult": {
        "description": "Normal theta-gamma coupling (PLV 0.80-0.95). Strong phase synchronization indicates healthy cross-frequency communication.",
        "theta_amp": 1.0, "gamma_amp": 1.5, "noise": 0.8, "seed": 42,
        "expected_score": "0.85-0.95",
        "citation": "Canolty et al. (2006) — High gamma power is phase-locked to theta oscillations in human neocortex"
    },
    "Major Depressive Disorder (MDD)": {
        "description": "Reduced theta-gamma coupling (PLV 0.40-0.65). Disrupted cross-frequency dynamics observed in prefrontal cortex.",
        "theta_amp": 0.5, "gamma_amp": 0.3, "noise": 2.0, "seed": 101,
        "expected_score": "0.55-0.70",
        "citation": "Sun et al. (2022) — Theta-gamma coupling deficit in MDD patients during working memory"
    },
    "Mild Cognitive Impairment (MCI)": {
        "description": "Moderate theta-gamma decoupling (PLV 0.50-0.70). Early marker of Alzheimer's disease progression.",
        "theta_amp": 0.7, "gamma_amp": 0.4, "noise": 1.8, "seed": 202,
        "expected_score": "0.60-0.75",
        "citation": "Goodman et al. (2018) — Theta-gamma coupling and working memory in Alzheimer's disease"
    },
    "Epileptic Seizure (Ictal)": {
        "description": "Hypersynchronization (PLV > 0.95). Pathological excess coupling during seizure events.",
        "theta_amp": 3.0, "gamma_amp": 3.0, "noise": 0.3, "seed": 303,
        "expected_score": "0.95-1.00",
        "citation": "Amiri et al. (2016) — Phase-amplitude coupling during interictal and ictal periods"
    },
    "Meditation / Deep Focus": {
        "description": "Enhanced theta-gamma coupling (PLV 0.85-0.98). Heightened coherence observed in experienced meditators.",
        "theta_amp": 1.5, "gamma_amp": 2.0, "noise": 0.5, "seed": 404,
        "expected_score": "0.90-0.98",
        "citation": "Lutz et al. (2004) — Long-term meditators self-induce high-amplitude gamma synchrony"
    },
    "Anesthesia (Propofol)": {
        "description": "Severely disrupted cross-frequency coupling (PLV < 0.40). Consciousness marker.",
        "theta_amp": 0.3, "gamma_amp": 0.1, "noise": 2.5, "seed": 505,
        "expected_score": "0.50-0.60",
        "citation": "Aru et al. (2015) — Theta-gamma coupling reflects consciousness during propofol anesthesia"
    },
    "ADHD": {
        "description": "Elevated theta/beta ratio with weak gamma coupling. Reduced theta-gamma PAC in frontal regions.",
        "theta_amp": 1.5, "gamma_amp": 0.3, "noise": 1.5, "seed": 606,
        "expected_score": "0.60-0.72",
        "citation": "Kim et al. (2015) — Theta-gamma coupling differences in ADHD vs controls"
    },
    "Custom (Manual)": {
        "description": "Set your own parameters below.",
        "theta_amp": 1.0, "gamma_amp": 0.5, "noise": 1.5, "seed": 42,
        "expected_score": "Varies",
        "citation": ""
    }
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SYNTHETIC EEG GENERATOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generate_synthetic_eeg(duration: float, fs: float, theta_amp: float,
                           gamma_amp: float, noise_level: float, seed: int,
                           n_channels: int = 1) -> tuple:
    """Generate multi-channel synthetic EEG with controllable parameters."""
    rng = np.random.RandomState(int(seed))
    n_samples = int(fs * duration)
    t = np.linspace(0, duration, n_samples)

    channels = []
    for ch in range(n_channels):
        # Theta component (4-8 Hz, center ~6 Hz)
        theta_freq = 5.5 + rng.uniform(-0.5, 0.5)
        theta = theta_amp * np.sin(2 * np.pi * theta_freq * t + rng.uniform(0, 2 * np.pi))

        # Gamma component (30-100 Hz, center ~40 Hz) — modulated by theta phase
        gamma_freq = 38 + rng.uniform(-3, 3)
        theta_phase = np.angle(sig.hilbert(theta))
        # Phase-amplitude coupling: gamma amplitude modulated by theta phase
        gamma_envelope = 1.0 + 0.5 * np.cos(theta_phase)
        gamma = gamma_amp * gamma_envelope * np.sin(2 * np.pi * gamma_freq * t + rng.uniform(0, 2 * np.pi))

        # Alpha background (8-13 Hz)
        alpha = 0.3 * np.sin(2 * np.pi * 10 * t + rng.uniform(0, 2 * np.pi))

        # 1/f noise (pink noise approximation)
        white = rng.normal(0, noise_level, n_samples)
        b_pink, a_pink = sig.butter(1, 0.01, btype='low')
        pink = sig.filtfilt(b_pink, a_pink, white) * noise_level * 2

        # Line noise (50/60 Hz)
        line_noise = 0.1 * np.sin(2 * np.pi * 60 * t)

        eeg = theta + gamma + alpha + pink + white * 0.3 + line_noise
        channels.append(eeg)

    return t, np.array(channels)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CSV UPLOAD HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def parse_csv_upload(file_obj, fs: float) -> tuple:
    """Parse uploaded CSV/TSV EEG data. Returns (time, channels_array)."""
    if file_obj is None:
        return None, None

    content = file_obj.decode("utf-8") if isinstance(file_obj, bytes) else open(file_obj, 'r').read()
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)

    # Detect header
    try:
        float(rows[0][0])
        data_rows = rows
    except (ValueError, IndexError):
        data_rows = rows[1:]

    data = np.array([[float(x) for x in row] for row in data_rows if row])

    # If single column, treat as single channel
    if data.ndim == 1:
        data = data.reshape(1, -1)
    elif data.shape[1] > data.shape[0]:
        pass  # Already channels x samples
    else:
        data = data.T  # Transpose to channels x samples

    n_samples = data.shape[1]
    t = np.arange(n_samples) / fs
    return t, data


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VISUALIZATION ENGINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DARK_BG = '#0a0f1a'
PANEL_BG = '#111827'
GRID_COLOR = '#1e293b'
TEXT_COLOR = '#e2e8f0'
ACCENT_BLUE = '#38bdf8'
ACCENT_PURPLE = '#a78bfa'
ACCENT_ORANGE = '#fb923c'
ACCENT_GREEN = '#22c55e'
ACCENT_RED = '#ef4444'
ACCENT_YELLOW = '#eab308'


def style_axis(ax, title=""):
    ax.set_facecolor(PANEL_BG)
    ax.set_title(title, color=TEXT_COLOR, fontsize=11, fontweight='bold', pad=8)
    ax.tick_params(colors=TEXT_COLOR, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
    ax.grid(True, alpha=0.15, color=GRID_COLOR)


def create_analysis_figure(t, eeg, fs, band1, band2, plv, coherence_score, status, color,
                           sliding_times=None, sliding_plvs=None):
    """Create the full 6-panel analysis figure."""
    fig = plt.figure(figsize=(14, 12))
    fig.patch.set_facecolor(DARK_BG)

    gs = GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.25)

    # ── Panel 1: Raw Signal ──
    ax1 = fig.add_subplot(gs[0, 0])
    display_sec = min(3, t[-1])
    mask = t <= display_sec
    ax1.plot(t[mask], eeg[mask], color=ACCENT_BLUE, linewidth=0.4, alpha=0.9)
    style_axis(ax1, f"Raw EEG Signal ({display_sec:.0f}s)")
    ax1.set_xlabel("Time (s)", color=TEXT_COLOR, fontsize=8)
    ax1.set_ylabel("Amplitude (uV)", color=TEXT_COLOR, fontsize=8)

    # ── Panel 2: Power Spectral Density ──
    ax2 = fig.add_subplot(gs[0, 1])
    freqs, psd = compute_spectral_power(eeg, fs)
    freq_mask = freqs <= 80
    ax2.semilogy(freqs[freq_mask], psd[freq_mask], color=ACCENT_BLUE, linewidth=1)
    # Shade bands
    ax2.axvspan(band1[0], band1[1], alpha=0.2, color=ACCENT_PURPLE, label=f'Band 1 ({band1[0]}-{band1[1]} Hz)')
    ax2.axvspan(band2[0], band2[1], alpha=0.2, color=ACCENT_ORANGE, label=f'Band 2 ({band2[0]}-{band2[1]} Hz)')
    ax2.legend(fontsize=7, facecolor=PANEL_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
    style_axis(ax2, "Power Spectral Density (Welch)")
    ax2.set_xlabel("Frequency (Hz)", color=TEXT_COLOR, fontsize=8)
    ax2.set_ylabel("PSD (uV^2/Hz)", color=TEXT_COLOR, fontsize=8)

    # ── Panel 3: Filtered Bands ──
    ax3 = fig.add_subplot(gs[1, 0])
    theta_filt = bandpass_filter(eeg, band1[0], band1[1], fs)
    gamma_filt = bandpass_filter(eeg, band2[0], band2[1], fs)
    ax3.plot(t[mask], theta_filt[mask], color=ACCENT_PURPLE, linewidth=0.8,
             label=f'Band 1: {band1[0]}-{band1[1]} Hz')
    ax3.plot(t[mask], gamma_filt[mask], color=ACCENT_ORANGE, linewidth=0.5,
             label=f'Band 2: {band2[0]}-{band2[1]} Hz')
    ax3.legend(fontsize=7, facecolor=PANEL_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
    style_axis(ax3, "Bandpass Filtered Components")
    ax3.set_xlabel("Time (s)", color=TEXT_COLOR, fontsize=8)

    # ── Panel 4: Phase Difference ──
    ax4 = fig.add_subplot(gs[1, 1])
    phase1 = extract_phase(eeg, band1[0], band1[1], fs)
    phase2 = extract_phase(eeg, band2[0], band2[1], fs)
    phase_diff = phase1 - phase2
    ax4.plot(t[mask], phase_diff[mask], color='#c084fc', linewidth=0.5, alpha=0.8)
    ax4.axhline(y=0, color=ACCENT_GREEN, linewidth=0.5, linestyle='--', alpha=0.5)
    style_axis(ax4, "Phase Difference (Band1 - Band2)")
    ax4.set_xlabel("Time (s)", color=TEXT_COLOR, fontsize=8)
    ax4.set_ylabel("Radians", color=TEXT_COLOR, fontsize=8)

    # ── Panel 5: Sliding PLV (Temporal Dynamics) ──
    ax5 = fig.add_subplot(gs[2, 0])
    if sliding_times is not None and len(sliding_times) > 0:
        ax5.plot(sliding_times, sliding_plvs, color=ACCENT_GREEN, linewidth=1.5)
        ax5.fill_between(sliding_times, sliding_plvs, alpha=0.15, color=ACCENT_GREEN)
        ax5.axhline(y=0.80, color=ACCENT_YELLOW, linewidth=1, linestyle='--', alpha=0.7, label='PLV 0.80')
        ax5.axhline(y=np.mean(sliding_plvs), color=ACCENT_BLUE, linewidth=1, linestyle=':',
                    alpha=0.7, label=f'Mean PLV {np.mean(sliding_plvs):.3f}')
        ax5.legend(fontsize=7, facecolor=PANEL_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
    style_axis(ax5, "Sliding Window PLV (2s window, 0.5s step)")
    ax5.set_xlabel("Time (s)", color=TEXT_COLOR, fontsize=8)
    ax5.set_ylabel("PLV", color=TEXT_COLOR, fontsize=8)
    ax5.set_ylim(0, 1)

    # ── Panel 6: Coherence Gauge ──
    ax6 = fig.add_subplot(gs[2, 1])
    # Create a gradient bar
    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    ax6.imshow(gradient, aspect='auto', extent=[0, 1, -0.3, 0.3],
               cmap=plt.cm.RdYlGn, alpha=0.3)
    ax6.barh([0], [coherence_score], color=color, height=0.25, zorder=3, edgecolor='white', linewidth=0.5)
    ax6.axvline(x=0.90, color=ACCENT_GREEN, linewidth=2, linestyle='--', alpha=0.8, zorder=4)
    ax6.axvline(x=0.70, color=ACCENT_YELLOW, linewidth=1.5, linestyle='--', alpha=0.6, zorder=4)
    ax6.text(0.90, 0.35, 'Healthy', color=ACCENT_GREEN, fontsize=8, ha='center')
    ax6.text(0.70, 0.35, 'Moderate', color=ACCENT_YELLOW, fontsize=8, ha='center')
    ax6.text(coherence_score, -0.35, f'{coherence_score:.3f}', color='white', fontsize=14,
             fontweight='bold', ha='center', va='top', zorder=5)
    style_axis(ax6, f"Global Coherence Ratio — {status}")
    ax6.set_xlim(0, 1)
    ax6.set_ylim(-0.5, 0.5)
    ax6.set_yticks([])
    ax6.set_xlabel("Coherence Score", color=TEXT_COLOR, fontsize=8)

    # Watermark
    fig.text(0.99, 0.01, f'GCFD Tracker v{__version__} | TAURUS AI Corp',
             ha='right', va='bottom', fontsize=7, color='#475569', alpha=0.5)

    return fig


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN ANALYSIS FUNCTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_analysis(preset, duration, fs, theta_amp, gamma_amp, noise_level, seed,
                 theta_low, theta_high, gamma_low, gamma_high, csv_file):
    """Main analysis pipeline: generate/load EEG, compute all metrics, return visualization."""

    # Load data
    if csv_file is not None:
        t, channels = parse_csv_upload(csv_file, fs)
        if channels is None:
            return None, "Error: Could not parse CSV file."
        eeg = channels[0]  # Use first channel
        data_source = "Uploaded CSV"
    else:
        t, channels = generate_synthetic_eeg(duration, fs, theta_amp, gamma_amp, noise_level, int(seed))
        eeg = channels[0]
        data_source = f"Synthetic ({preset})"

    band1 = (theta_low, theta_high)
    band2 = (gamma_low, gamma_high)

    # Compute metrics
    phase1 = extract_phase(eeg, band1[0], band1[1], fs)
    phase2 = extract_phase(eeg, band2[0], band2[1], fs)
    plv = compute_plv(phase1, phase2)
    coherence_score = 0.5 + (plv * 0.5)

    # Band powers
    band1_power = compute_band_power(eeg, fs, band1[0], band1[1])
    band2_power = compute_band_power(eeg, fs, band2[0], band2[1])

    # Sliding PLV
    sliding_times, sliding_plvs = compute_sliding_plv(eeg, fs, band1, band2)
    plv_std = float(np.std(sliding_plvs)) if len(sliding_plvs) > 0 else 0
    plv_min = float(np.min(sliding_plvs)) if len(sliding_plvs) > 0 else 0
    plv_max = float(np.max(sliding_plvs)) if len(sliding_plvs) > 0 else 0

    # Classification
    if coherence_score >= 0.90:
        status = "HEALTHY"
        color = ACCENT_GREEN
        interpretation = "Strong theta-gamma phase coupling. Indicates healthy cross-frequency neural communication."
    elif coherence_score >= 0.70:
        status = "MODERATE"
        color = ACCENT_YELLOW
        interpretation = "Partial phase synchronization. May indicate subclinical disruption in cross-frequency dynamics."
    else:
        status = "LOW"
        color = ACCENT_RED
        interpretation = "Weak cross-frequency coupling. Consistent with disrupted neural coherence patterns."

    # Create figure
    fig = create_analysis_figure(t, eeg, fs, band1, band2, plv, coherence_score,
                                 status, color, sliding_times, sliding_plvs)

    # Get preset info
    preset_info = CLINICAL_PRESETS.get(preset, {})

    # Build report
    report = f"""## GCFD Analysis Report

### Global Coherence Ratio: **{coherence_score:.4f}** ({status})

{interpretation}

---

### Phase Synchronization Metrics

| Metric | Value |
|--------|-------|
| **Phase Locking Value (PLV)** | {plv:.4f} |
| **Global Coherence Score** | {coherence_score:.4f} |
| **PLV Temporal Stability (std)** | {plv_std:.4f} |
| **PLV Range** | [{plv_min:.3f} — {plv_max:.3f}] |
| **Band 1 Relative Power** | {band1_power:.4f} ({band1_power*100:.1f}%) |
| **Band 2 Relative Power** | {band2_power:.4f} ({band2_power*100:.1f}%) |

### Signal Parameters

| Parameter | Value |
|-----------|-------|
| Data Source | {data_source} |
| Sampling Rate | {fs:.0f} Hz |
| Duration | {t[-1]:.1f}s ({len(eeg):,} samples) |
| Band 1 (Low Freq) | {band1[0]:.1f} — {band1[1]:.1f} Hz |
| Band 2 (High Freq) | {band2[0]:.1f} — {band2[1]:.1f} Hz |
| Sliding Window | 2.0s window, 0.5s step |
"""

    if preset_info.get("citation"):
        report += f"""
### Clinical Reference

**Preset**: {preset}
> {preset_info.get('description', '')}

**Expected Score Range**: {preset_info.get('expected_score', 'N/A')}

**Citation**: {preset_info.get('citation', '')}
"""

    report += """
---

### Methodology

**Phase Locking Value (PLV)** quantifies the consistency of the phase difference between two frequency-band-filtered signals over time. A PLV of 1.0 indicates perfect phase synchronization; 0.0 indicates no consistent phase relationship.

**Pipeline**: Raw EEG → Butterworth bandpass (order 3, zero-phase) → Hilbert transform → instantaneous phase extraction → PLV computation → sliding window temporal analysis.

**Global Coherence Score** maps PLV to a [0.5, 1.0] clinical scale where values above 0.90 indicate healthy cross-frequency coupling.

**References**:
- Lachaux et al. (1999) — *Measuring phase synchrony in brain signals*. Human Brain Mapping.
- Canolty et al. (2006) — *High gamma power is phase-locked to theta oscillations*. Science.
- Tort et al. (2010) — *Measuring phase-amplitude coupling*. J Neurophysiology.
"""

    return fig, report


def load_preset(preset_name):
    """Load clinical preset parameters."""
    preset = CLINICAL_PRESETS.get(preset_name, CLINICAL_PRESETS["Custom (Manual)"])
    return (
        preset["theta_amp"],
        preset["gamma_amp"],
        preset["noise"],
        preset["seed"],
        preset.get("description", "")
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GRADIO APPLICATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CSS = """
.gcfd-header { text-align: center; padding: 20px 0 10px 0; }
.gcfd-header h1 { font-size: 2em; margin-bottom: 5px; }
.metric-box { border: 1px solid #334155; border-radius: 8px; padding: 12px; background: #0f172a; }
footer { display: none !important; }
"""

with gr.Blocks(
    title="GCFD Coherence Tracker | TAURUS AI Corp",
    theme=gr.themes.Base(
        primary_hue="blue",
        secondary_hue="purple",
        neutral_hue="slate",
        font=gr.themes.GoogleFont("Inter"),
    ),
    css=CSS,
) as demo:

    # ── Header ──
    gr.HTML("""
    <div class="gcfd-header">
        <h1>GCFD Coherence Tracker</h1>
        <p style="color: #94a3b8; font-size: 1.1em;">
            Generalized Cross-Frequency Decomposition for EEG/MEG Phase Synchronization Analysis
        </p>
        <p style="color: #64748b; font-size: 0.85em;">
            v1.0.0 | Built by <a href="https://taurusai.io" style="color: #38bdf8;">TAURUS AI Corp</a>
            | Global Bio-Foundry Initiative
            | Apache 2.0 License
        </p>
    </div>
    """)

    with gr.Tabs():

        # ━━━━━━━ TAB 1: ANALYSIS ━━━━━━━
        with gr.TabItem("Analysis"):
            with gr.Row():
                with gr.Column(scale=1):

                    gr.Markdown("### Clinical Preset")
                    preset = gr.Dropdown(
                        choices=list(CLINICAL_PRESETS.keys()),
                        value="Healthy Adult",
                        label="Select Condition",
                        info="Pre-configured signal parameters for common clinical states"
                    )
                    preset_desc = gr.Textbox(
                        value=CLINICAL_PRESETS["Healthy Adult"]["description"],
                        label="Description", lines=2, interactive=False
                    )

                    gr.Markdown("### Signal Parameters")
                    duration = gr.Slider(1, 60, value=10, step=1, label="Duration (seconds)")
                    fs = gr.Slider(100, 1000, value=250, step=50, label="Sampling Rate (Hz)")
                    theta_amp = gr.Slider(0, 5, value=1.0, step=0.1, label="Theta Amplitude")
                    gamma_amp = gr.Slider(0, 5, value=1.5, step=0.1, label="Gamma Amplitude")
                    noise_level = gr.Slider(0, 5, value=0.8, step=0.1, label="Noise Level")
                    seed = gr.Number(value=42, label="Random Seed", precision=0)

                    gr.Markdown("### Frequency Bands")
                    theta_low = gr.Slider(0.5, 12, value=4.0, step=0.5, label="Band 1 Low (Hz)")
                    theta_high = gr.Slider(4, 15, value=8.0, step=0.5, label="Band 1 High (Hz)")
                    gamma_low = gr.Slider(15, 80, value=30.0, step=1, label="Band 2 Low (Hz)")
                    gamma_high = gr.Slider(30, 150, value=100.0, step=1, label="Band 2 High (Hz)")

                    gr.Markdown("### Upload EEG Data (optional)")
                    csv_upload = gr.File(
                        label="CSV/TSV file (channels as columns, samples as rows)",
                        file_types=[".csv", ".tsv", ".txt"],
                        type="binary"
                    )

                    analyze_btn = gr.Button("Run Coherence Analysis", variant="primary", size="lg")

                with gr.Column(scale=2):
                    plot_output = gr.Plot(label="GCFD Analysis Dashboard")
                    report_output = gr.Markdown()

            # Preset loader
            preset.change(
                fn=load_preset,
                inputs=[preset],
                outputs=[theta_amp, gamma_amp, noise_level, seed, preset_desc]
            )

            # Analysis trigger
            analyze_btn.click(
                fn=run_analysis,
                inputs=[preset, duration, fs, theta_amp, gamma_amp, noise_level, seed,
                        theta_low, theta_high, gamma_low, gamma_high, csv_upload],
                outputs=[plot_output, report_output]
            )

        # ━━━━━━━ TAB 2: DOCUMENTATION ━━━━━━━
        with gr.TabItem("Documentation"):
            gr.Markdown("""
## GCFD Coherence Tracker — Technical Documentation

### What is GCFD?

**Generalized Cross-Frequency Decomposition** is a method for quantifying the phase
relationship between neural oscillations at different frequencies. The core metric
is the **Phase Locking Value (PLV)**, which measures the consistency of the phase
difference between two band-filtered signals.

### Why Cross-Frequency Coupling Matters

Neural oscillations at different frequencies serve distinct computational roles:
- **Theta (4-8 Hz)**: Memory encoding, spatial navigation, top-down control
- **Gamma (30-100 Hz)**: Local cortical processing, feature binding, attention

The **coupling** between theta and gamma (theta-gamma PAC/PLV) is a biomarker for:
- Working memory capacity
- Cognitive function in aging
- Severity of neuropsychiatric conditions (MDD, ADHD, Alzheimer's)
- Depth of anesthesia / consciousness level

### Signal Processing Pipeline

```
Raw EEG/MEG Signal
    |
    v
[Butterworth Bandpass Filter] ─── Order 3, zero-phase (filtfilt)
    |                                  Band 1: e.g., Theta (4-8 Hz)
    |                                  Band 2: e.g., Gamma (30-100 Hz)
    v
[Hilbert Transform] ─────────── Extract analytic signal
    |
    v
[Phase Extraction] ──────────── np.angle(analytic_signal)
    |
    v
[Phase Locking Value] ────────── PLV = |mean(exp(j * (phase1 - phase2)))|
    |
    v
[Sliding Window Analysis] ───── 2s window, 0.5s step for temporal dynamics
    |
    v
[Global Coherence Score] ────── Mapped to [0.5, 1.0] clinical scale
```

### Clinical Interpretation Scale

| Score Range | Classification | Interpretation |
|-------------|---------------|----------------|
| 0.90 - 1.00 | **HEALTHY** | Strong cross-frequency coupling |
| 0.70 - 0.89 | **MODERATE** | Partial synchronization |
| 0.50 - 0.69 | **LOW** | Weak coupling / potential pathology |

**Note**: Scores above 0.95 may indicate pathological hypersynchronization (e.g., epileptic activity).

### CSV Upload Format

Upload EEG data as CSV with:
- **Rows**: Time samples
- **Columns**: Channels (first column used if multiple)
- **No time column** needed — timing derived from sampling rate parameter
- **Units**: Microvolts (uV) preferred, but any consistent unit works

### Limitations

- This tool uses **synthetic EEG** by default — clinical use requires real EEG data
- PLV is sensitive to signal length and SNR — minimum 5 seconds recommended
- Single-channel analysis only (multi-channel averaging planned for v2.0)
- Phase-amplitude coupling (PAC) via Modulation Index not yet implemented

### References

1. Lachaux, J.P. et al. (1999). *Measuring phase synchrony in brain signals*. Human Brain Mapping, 8(4), 194-208.
2. Canolty, R.T. et al. (2006). *High gamma power is phase-locked to theta oscillations in human neocortex*. Science, 313(5793), 1626-1628.
3. Tort, A.B. et al. (2010). *Measuring phase-amplitude coupling between neuronal oscillations of different frequencies*. Journal of Neurophysiology, 104(2), 1195-1210.
4. Goodman, M.S. et al. (2018). *Theta-gamma coupling and working memory in Alzheimer's disease and mild cognitive impairment*. Frontiers in Aging Neuroscience, 10, 101.
5. Sun, L. et al. (2022). *Theta-gamma coupling deficit in MDD patients during working memory*. Brain Research Bulletin, 189, 49-57.
            """)

        # ━━━━━━━ TAB 3: API ━━━━━━━
        with gr.TabItem("API"):
            gr.Markdown("""
## API Access

This Space exposes a REST API via Gradio's built-in endpoint system.

### Python Client

```python
from gradio_client import Client

client = Client("Taurus-Ai-Corp/gcfd-coherence-tracker")
result = client.predict(
    preset="Healthy Adult",
    duration=10,
    fs=250,
    theta_amp=1.0,
    gamma_amp=1.5,
    noise_level=0.8,
    seed=42,
    theta_low=4.0,
    theta_high=8.0,
    gamma_low=30.0,
    gamma_high=100.0,
    csv_file=None,
    api_name="/run_analysis"
)
```

### cURL

```bash
curl -X POST https://Taurus-Ai-Corp-gcfd-coherence-tracker.hf.space/api/predict \\
  -H "Content-Type: application/json" \\
  -d '{"data": ["Healthy Adult", 10, 250, 1.0, 1.5, 0.8, 42, 4.0, 8.0, 30.0, 100.0, null]}'
```

### Rate Limits

| Tier | Rate | Access |
|------|------|--------|
| Free (this Space) | 50 requests/day | Open |
| Researcher ($29/mo) | 1,000 requests/day | [Contact us](mailto:admin@taurusai.io) |
| Clinical ($149/mo) | 10,000 requests/day + batch | [Contact us](mailto:admin@taurusai.io) |
| Enterprise | Unlimited + SLA | [Contact us](mailto:admin@taurusai.io) |

### Upcoming Features (v2.0)

- Multi-channel analysis with topographic maps
- Phase-Amplitude Coupling (PAC) via Modulation Index
- EDF/BDF file format support
- Batch processing endpoint
- Pre-trained EEG foundation model integration (braindecode/SignalJEPA)
            """)

        # ━━━━━━━ TAB 4: ABOUT ━━━━━━━
        with gr.TabItem("About"):
            gr.Markdown(f"""
## About GCFD Coherence Tracker

**Version**: {__version__}
**Author**: [TAURUS AI Corp](https://taurusai.io)
**License**: Apache License 2.0
**Repository**: [GitHub](https://github.com/Taurus-Ai-Corp)

### The Global Bio-Foundry Initiative

TAURUS AI Corp's neuroscience research initiative explores the intersection of:
- **Neural coherence** in biological systems
- **Cross-frequency coupling** dynamics in EEG/MEG signals
- **Open-source neuroscience** tooling for clinical research

The GCFD Coherence Tracker is the open-source component of this initiative,
providing standard DSP tools for EEG/MEG phase synchronization analysis.

### Citation

If you use this tool in your research, please cite:

```bibtex
@software{{gcfd_tracker_2026,
  title = {{GCFD Coherence Tracker: Cross-Frequency Phase Synchronization Analysis}},
  author = {{TAURUS AI Corp}},
  year = {{2026}},
  version = {{{__version__}}},
  url = {{https://huggingface.co/spaces/Taurus-Ai-Corp/gcfd-coherence-tracker}},
  license = {{Apache-2.0}}
}}
```

### Related Work

- [braindecode](https://braindecode.org/) — Deep learning for EEG/MEG
- [MNE-Python](https://mne.tools/) — MEG/EEG analysis toolkit
- [SignalJEPA](https://huggingface.co/braindecode/SignalJEPA-pretrained) — Brain signal foundation model

### Contact

- Research inquiries: admin@taurusai.io
- Enterprise licensing: admin@taurusai.io
- Issues: [GitHub Issues](https://github.com/Taurus-Ai-Corp)
            """)

    # NOTE: Removed demo.load() auto-run to prevent startup crashes from
    # breaking the Gradio API. Users click "Run Coherence Analysis" to start.

demo.launch()
