"""Full 4-stage PAC analysis pipeline.

PACAnalyzer is the primary entry point for signal analysis. It chains:
  Stage 1: Butterworth bandpass (reduces spurious PAC from sharp transients)
  Stage 2: Tort MI + MVL computation
  Stage 3: Surrogate significance testing (Tort et al. 2010, 95th pctile)
  Stage 4: Effect-size thresholding (MI > min_mi = 0.01)

Standalone pipeline suitable for any EEG phase-amplitude coupling analysis.
"""
import numpy as np
import scipy.signal as signal

from .modulation_index import compute_mi, compute_mvl
from .artifact_rejection import compute_surrogate_threshold, is_artifactual_pac


class PACAnalyzer:
    """Standalone PAC engine: Tort MI with 4-stage artifact rejection.

    Usage:
        analyzer = PACAnalyzer(fs=250)
        result = analyzer.analyze(raw_eeg)
        # result: {mi, mvl, is_genuine, surrogate_threshold, reason}
    """

    def __init__(
        self,
        fs: float = 250.0,
        theta_band: tuple = (4.0, 8.0),
        gamma_band: tuple = (30.0, 100.0),
        n_bins: int = 18,
        n_surrogates: int = 200,
        min_mi: float = 0.01,
        surrogate_percentile: float = 95.0,
    ):
        self.fs = fs
        self.theta_band = theta_band
        self.gamma_band = gamma_band
        self.n_bins = n_bins
        self.n_surrogates = n_surrogates
        self.min_mi = min_mi
        self.surrogate_percentile = surrogate_percentile

    def _bandpass(self, data: np.ndarray, band: tuple) -> np.ndarray:
        nyq = self.fs / 2
        lo = max(0.01, band[0] / nyq)
        hi = min(0.99, band[1] / nyq)
        b, a = signal.butter(3, [lo, hi], btype="band")
        return signal.filtfilt(b, a, data)

    def extract_phase(self, data: np.ndarray) -> np.ndarray:
        """Instantaneous theta phase via Hilbert transform."""
        return np.angle(signal.hilbert(self._bandpass(data, self.theta_band)))

    def extract_amplitude(self, data: np.ndarray) -> np.ndarray:
        """Instantaneous gamma amplitude envelope via Hilbert transform."""
        return np.abs(signal.hilbert(self._bandpass(data, self.gamma_band)))

    def analyze(
        self,
        raw: np.ndarray,
        rng=None,
    ) -> dict:
        """Run full 4-stage pipeline on raw EEG segment.

        Args:
            raw: 1-D raw EEG array (minimum ~4 seconds at fs=250 recommended)
            rng: Random generator for reproducible surrogate sampling

        Returns:
            dict with keys: mi, mvl, is_genuine, surrogate_threshold, reason
        """
        if rng is None:
            rng = np.random.default_rng()

        if raw.ndim > 1:
            raw = raw[0]

        theta_phase = self.extract_phase(raw)
        gamma_amp = self.extract_amplitude(raw)

        mi = compute_mi(theta_phase, gamma_amp, self.n_bins)
        mvl = compute_mvl(theta_phase, gamma_amp)

        threshold, _ = compute_surrogate_threshold(
            theta_phase, gamma_amp,
            n_surrogates=self.n_surrogates,
            percentile=self.surrogate_percentile,
            n_bins=self.n_bins,
            rng=rng,
        )

        genuine, reason = is_artifactual_pac(
            theta_phase, gamma_amp, mi, threshold, self.min_mi
        )

        return {
            "mi": mi,
            "mvl": mvl,
            "is_genuine": genuine,
            "surrogate_threshold": threshold,
            "reason": reason,
        }
