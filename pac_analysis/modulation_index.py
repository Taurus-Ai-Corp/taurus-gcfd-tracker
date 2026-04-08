"""Modulation Index and Mean Vector Length for phase-amplitude coupling.

References:
  Tort et al. (2010). "Measuring phase-amplitude coupling between neuronal
    oscillations of different frequencies." J Neurophysiology 104:1195-1210.
  Canolty et al. (2006). "High gamma power is phase-locked to theta oscillations
    in human neocortex." Science 313:1626-1628.
"""
import numpy as np
import scipy.signal as signal


def compute_mi(
    phase_signal: np.ndarray,
    amp_signal: np.ndarray,
    n_bins: int = 18,
) -> float:
    """Tort Modulation Index via KL divergence (Tort et al. 2010).

    Divides one theta cycle into n_bins phase bins. Mean amplitude per bin
    forms a distribution P. MI = KL(P || U) / log(n_bins), where U is uniform.

    Range: 0.0 (no coupling) to 1.0 (perfect coupling).
    """
    bins = np.linspace(-np.pi, np.pi, n_bins + 1)
    amp_per_bin = np.zeros(n_bins)
    for i in range(n_bins):
        mask = (phase_signal >= bins[i]) & (phase_signal < bins[i + 1])
        amp_per_bin[i] = np.mean(amp_signal[mask]) if np.any(mask) else 0.0

    total = amp_per_bin.sum()
    if total < 1e-10:
        return 0.0

    p = amp_per_bin / total                       # normalized distribution
    q = np.ones(n_bins) / n_bins                  # uniform reference
    kl = np.sum(p * np.log(p / q + 1e-12))        # KL divergence (nats)
    return float(kl / np.log(n_bins))             # normalize to [0, 1]


def compute_mvl(
    phase_signal: np.ndarray,
    amp_signal: np.ndarray,
) -> float:
    """Normalized Mean Vector Length (Cohen 2008; cf. Canolty et al. 2006).

    Normalized form: |mean(A * exp(iφ))| / mean(A) — bounded in [0,1].
    Original Canolty 2006 uses unnormalized |mean(A * exp(iφ))|; normalization
    by mean(A) is from Cohen (2008), enabling cross-signal comparison.
    O(n) vs O(n*bins) — preferred for real-time use.
    """
    mean_amp = np.mean(amp_signal)
    if mean_amp < 1e-10:
        return 0.0
    return float(
        np.abs(np.mean(amp_signal * np.exp(1j * phase_signal))) / mean_amp
    )


def comodulogram(
    raw: np.ndarray,
    fs: float,
    phase_freqs: tuple = (2.0, 20.0, 2.0),
    amp_freqs: tuple = (20.0, 100.0, 10.0),
    n_bins: int = 18,
    bw_phase: float = 2.0,
    bw_amp: float = 5.0,
) -> tuple:
    """Full phase-amplitude comodulogram.

    Args:
        raw: 1-D raw EEG array.
        fs: Sampling frequency (Hz).
        phase_freqs: (start, stop, step) for phase frequency grid.
        amp_freqs: (start, stop, step) for amplitude frequency grid.
        n_bins: Phase bins for MI computation.
        bw_phase: Filter half-bandwidth for phase signal extraction (Hz). Default 2.0.
        bw_amp: Filter half-bandwidth for amplitude envelope extraction (Hz). Default 5.0.

    Returns:
        (mi_matrix, phase_centers, amp_centers)
        mi_matrix[i, j] = MI(phase_freqs[i], amp_freqs[j])
    """
    phase_centers = np.arange(phase_freqs[0], phase_freqs[1], phase_freqs[2]) + phase_freqs[2] / 2
    amp_centers = np.arange(amp_freqs[0], amp_freqs[1], amp_freqs[2]) + amp_freqs[2] / 2
    mi_matrix = np.zeros((len(phase_centers), len(amp_centers)))
    nyq = fs / 2

    for i, fp in enumerate(phase_centers):
        lo = max(0.01, (fp - bw_phase) / nyq)
        hi = min(0.99, (fp + bw_phase) / nyq)
        b, a = signal.butter(3, [lo, hi], btype="band")
        phase_sig = np.angle(signal.hilbert(signal.filtfilt(b, a, raw)))

        for j, fa in enumerate(amp_centers):
            lo_a = max(0.01, (fa - bw_amp) / nyq)
            hi_a = min(0.99, (fa + bw_amp) / nyq)
            b_a, a_a = signal.butter(3, [lo_a, hi_a], btype="band")
            amp_sig = np.abs(signal.hilbert(signal.filtfilt(b_a, a_a, raw)))
            mi_matrix[i, j] = compute_mi(phase_sig, amp_sig, n_bins)

    return mi_matrix, phase_centers, amp_centers
