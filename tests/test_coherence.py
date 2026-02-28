"""Test suite for taurus-gcfd-tracker core coherence analysis.

Tests the CoherenceTracker class (taurus_gcfd.py) and DSP functions (app/app.py).
Required for JOSS submission: automated tests verifying correctness.
"""

import sys
import os
import numpy as np
import pytest

# Add repo root to path so imports work from any directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from taurus_gcfd import CoherenceTracker, datasets


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Core CoherenceTracker Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestCoherenceTracker:
    """Tests for the core CoherenceTracker class."""

    def setup_method(self):
        self.tracker = CoherenceTracker(sampling_rate=250)

    def test_coherence_score_in_valid_range(self):
        """Coherence score must be in [0.0, 1.0] for any input."""
        data = datasets.load_sample_eeg("test")
        score = self.tracker.calculate_global_coherence(data)
        assert 0.0 <= score <= 1.0, f"Score {score} outside [0, 1]"

    def test_deterministic_output(self):
        """Same input must produce identical output (no hidden randomness)."""
        data = datasets.load_sample_eeg("patient_01")
        score1 = self.tracker.calculate_global_coherence(data)
        score2 = self.tracker.calculate_global_coherence(data)
        assert score1 == score2, "Non-deterministic output detected"

    def test_2d_input_uses_first_channel(self):
        """2D array input should use first channel without crashing."""
        data_1d = datasets.load_sample_eeg("test")
        data_2d = np.vstack([data_1d, data_1d * 0.5])  # 2 channels
        score_1d = self.tracker.calculate_global_coherence(data_1d)
        score_2d = self.tracker.calculate_global_coherence(data_2d)
        assert score_1d == score_2d, "2D input not correctly using first channel"

    def test_custom_bands(self):
        """Custom frequency bands (alpha-gamma) should produce valid scores."""
        data = datasets.load_sample_eeg("test")
        score = self.tracker.calculate_global_coherence(
            data, band1=(8, 13), band2=(30, 100)
        )
        assert 0.0 <= score <= 1.0, f"Custom band score {score} outside [0, 1]"

    def test_pure_noise_low_coherence(self):
        """Pure random noise should produce low-to-moderate coherence (no phase locking)."""
        rng = np.random.RandomState(99)
        noise = rng.normal(0, 1, 2500)  # 10 sec at 250 Hz
        score = self.tracker.calculate_global_coherence(noise)
        assert score < 0.90, f"Pure noise scored {score} — expected < 0.90"

    def test_different_sampling_rates(self):
        """Tracker should handle different valid sampling rates without errors.

        Note: fs must be > 2× the highest band frequency (Nyquist theorem).
        Default gamma band goes to 100 Hz, so fs >= 250 Hz is required.
        """
        for fs in [250, 500, 1000]:
            tracker = CoherenceTracker(sampling_rate=fs)
            t = np.linspace(0, 5, fs * 5)
            signal = np.sin(2 * np.pi * 6 * t) + 0.5 * np.sin(2 * np.pi * 40 * t)
            score = tracker.calculate_global_coherence(signal)
            assert 0.0 <= score <= 1.0, f"Failed at fs={fs}: score={score}"

    def test_short_signal_does_not_crash(self):
        """Very short signals should not raise exceptions."""
        short = np.sin(np.linspace(0, 1, 250))  # 1 second at 250 Hz
        score = self.tracker.calculate_global_coherence(short)
        assert 0.0 <= score <= 1.0

    def test_datasets_load_returns_correct_shape(self):
        """Sample EEG loader should return 1D array of expected length."""
        data = datasets.load_sample_eeg("any_id")
        assert data.ndim == 1, f"Expected 1D, got {data.ndim}D"
        assert len(data) == 2500, f"Expected 2500 samples (10s @ 250Hz), got {len(data)}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# App DSP Function Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestAppDSP:
    """Tests for the DSP functions in app/app.py."""

    @pytest.fixture(autouse=True)
    def import_app(self):
        """Import app functions, skip if gradio not installed."""
        sys.path.insert(0, os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"
        ))
        try:
            from app import (
                bandpass_filter, extract_phase, compute_plv,
                compute_sliding_plv, generate_synthetic_eeg,
                CLINICAL_PRESETS
            )
            self.bandpass_filter = bandpass_filter
            self.extract_phase = extract_phase
            self.compute_plv = compute_plv
            self.compute_sliding_plv = compute_sliding_plv
            self.generate_synthetic_eeg = generate_synthetic_eeg
            self.CLINICAL_PRESETS = CLINICAL_PRESETS
        except ImportError:
            pytest.skip("gradio not installed — skipping app DSP tests")

    def test_bandpass_filter_output_shape(self):
        """Bandpass filter should preserve input array shape."""
        data = np.random.randn(2500)
        filtered = self.bandpass_filter(data, 4, 8, 250)
        assert filtered.shape == data.shape

    def test_bandpass_invalid_range_returns_zeros(self):
        """Invalid band range (low >= high) should return zeros."""
        data = np.random.randn(2500)
        result = self.bandpass_filter(data, 10, 5, 250)  # low > high
        assert np.allclose(result, 0)

    def test_plv_range(self):
        """PLV must be in [0, 1]."""
        phase1 = np.random.uniform(-np.pi, np.pi, 1000)
        phase2 = np.random.uniform(-np.pi, np.pi, 1000)
        plv = self.compute_plv(phase1, phase2)
        assert 0.0 <= plv <= 1.0

    def test_plv_identical_phases(self):
        """Identical phases should give PLV = 1.0."""
        phase = np.linspace(0, 4 * np.pi, 1000)
        plv = self.compute_plv(phase, phase)
        assert abs(plv - 1.0) < 0.01, f"Identical phases gave PLV={plv}"

    def test_sliding_plv_output_shapes(self):
        """Sliding PLV should return matching time and PLV arrays."""
        rng = np.random.RandomState(42)
        data = rng.randn(2500)  # 10 sec at 250 Hz
        times, plvs = self.compute_sliding_plv(data, 250, (4, 8), (30, 100))
        assert len(times) == len(plvs)
        assert len(times) > 0

    def test_synthetic_eeg_shape(self):
        """Synthetic EEG should return correct shapes."""
        t, channels = self.generate_synthetic_eeg(
            duration=5, fs=250, theta_amp=1.0,
            gamma_amp=1.0, noise_level=1.0, seed=42
        )
        assert t.shape == (1250,), f"Time shape: {t.shape}"
        assert channels.shape == (1, 1250), f"Channels shape: {channels.shape}"

    def test_synthetic_eeg_deterministic(self):
        """Same seed should produce identical synthetic EEG."""
        _, ch1 = self.generate_synthetic_eeg(5, 250, 1.0, 1.0, 1.0, seed=42)
        _, ch2 = self.generate_synthetic_eeg(5, 250, 1.0, 1.0, 1.0, seed=42)
        assert np.array_equal(ch1, ch2), "Synthetic EEG not deterministic"

    def test_all_presets_generate_valid_eeg(self):
        """Each clinical preset should generate valid EEG data."""
        for name, preset in self.CLINICAL_PRESETS.items():
            _, channels = self.generate_synthetic_eeg(
                duration=5, fs=250,
                theta_amp=preset["theta_amp"],
                gamma_amp=preset["gamma_amp"],
                noise_level=preset["noise"],
                seed=preset["seed"]
            )
            assert not np.any(np.isnan(channels)), f"NaN in preset '{name}'"
            assert not np.any(np.isinf(channels)), f"Inf in preset '{name}'"
