"""4-stage artifact rejection for PAC analysis.

Implements the protocol addressing Aru et al. (2015) criticisms of spurious
PAC in consumer-grade EEG.

Stage 1: Waveform shape control — handled upstream by PACAnalyzer bandpass
Stage 2: Surrogate statistics — time-shift surrogates (Tort et al. 2010)
Stage 3: Phase-shuffled null model — tonic vs phasic coupling test
Stage 4: Effect-size thresholding — minimum MI > 0.01

References:
  Tort et al. (2010). J Neurophysiol 104:1195-1210.
  Aru et al. (2015). Current Opinion in Neurobiology 31:51-61.
"""
import numpy as np
from .modulation_index import compute_mi


def compute_surrogate_threshold(
    phase_signal: np.ndarray,
    amp_signal: np.ndarray,
    n_surrogates: int = 200,
    percentile: float = 95.0,
    n_bins: int = 18,
    rng=None,
) -> tuple:
    """Time-shift surrogate significance threshold (Tort et al. 2010).

    Shifts amplitude envelope by random τ ∈ [T/4, 3T/4] (breaks phase
    relationship while preserving temporal autocorrelation). Builds null
    distribution of MI. Threshold = 95th percentile of null distribution.

    Returns:
        (threshold, surrogate_mi_array)
    """
    if rng is None:
        rng = np.random.default_rng()
    n = len(phase_signal)
    quarter = n // 4
    surrogate_mis = np.zeros(n_surrogates)
    for k in range(n_surrogates):
        shift = int(rng.integers(quarter, 3 * quarter))
        amp_shifted = np.roll(amp_signal, shift)
        surrogate_mis[k] = compute_mi(phase_signal, amp_shifted, n_bins)
    return float(np.percentile(surrogate_mis, percentile)), surrogate_mis


def compute_phase_shuffle_null(
    phase_signal: np.ndarray,
    amp_signal: np.ndarray,
    n_shuffles: int = 200,
    n_bins: int = 18,
    rng=None,
) -> tuple:
    """Phase-shuffle null model.

    Independently permutes theta phase vector — removes any coupling between
    phase and amplitude while preserving marginal distributions. Tests whether
    observed coupling is specific to phase-amplitude relationship (tonic coupling)
    vs. trial-level structure.

    Returns:
        (threshold_95th, shuffle_mi_array)
    """
    if rng is None:
        rng = np.random.default_rng()
    shuffle_mis = np.zeros(n_shuffles)
    for k in range(n_shuffles):
        phase_shuffled = rng.permutation(phase_signal)
        shuffle_mis[k] = compute_mi(phase_shuffled, amp_signal, n_bins)
    return float(np.percentile(shuffle_mis, 95.0)), shuffle_mis


def is_artifactual_pac(
    phase_signal: np.ndarray,
    amp_signal: np.ndarray,
    mi: float,
    surrogate_threshold: float,
    min_mi: float = 0.01,
) -> tuple:
    """Determine if observed MI is statistically genuine (stage 2 + 4 gates).

    Stage 4 (effect size): MI must exceed min_mi (neurologically trivial threshold).
    Stage 2 (significance): MI must exceed surrogate 95th percentile.

    Returns:
        (is_genuine, explanation_string)
    """
    if mi < min_mi:
        return False, f"MI={mi:.4f} below effect-size floor (min_mi={min_mi})"
    if mi <= surrogate_threshold:
        return False, f"MI={mi:.4f} not > surrogate 95th={surrogate_threshold:.4f}"
    return True, f"MI={mi:.4f} significant (surrogate_threshold={surrogate_threshold:.4f})"
