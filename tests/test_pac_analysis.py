import numpy as np
import pytest


def _make_coupled_signals(coupling=0.9, fs=250, duration=10.0, seed=42):
    rng = np.random.default_rng(seed)
    t = np.arange(0, duration, 1 / fs)
    theta_phase = 2 * np.pi * 6 * t
    phase_sig = (theta_phase % (2 * np.pi)) - np.pi
    amp_sig = 1.0 + coupling * np.cos(phase_sig)
    return phase_sig, amp_sig


def _make_raw_eeg_pac(coupling=0.6, fs=250, duration=10.0, seed=42):
    import scipy.signal as scipy_signal
    rng = np.random.default_rng(seed)
    t = np.arange(0, duration, 1 / fs)
    theta = np.sin(2 * np.pi * 6 * t)
    theta_phase = np.angle(scipy_signal.hilbert(theta))
    gamma_env = 1.0 + coupling * np.cos(theta_phase)
    gamma = gamma_env * np.sin(2 * np.pi * 40 * t)
    noise = rng.normal(0, 0.2, len(t))
    return theta + gamma + noise


# ── modulation_index ──

def test_mi_high_for_coupled_signal():
    from pac_analysis.modulation_index import compute_mi
    phase_sig, amp_sig = _make_coupled_signals(coupling=0.9)
    mi = compute_mi(phase_sig, amp_sig, n_bins=18)
    assert mi > 0.05

def test_mi_low_for_uncoupled_signal():
    from pac_analysis.modulation_index import compute_mi
    rng = np.random.default_rng(0)
    phase_sig = rng.uniform(-np.pi, np.pi, 2500)
    amp_sig = rng.uniform(0.5, 1.5, 2500)
    mi = compute_mi(phase_sig, amp_sig, n_bins=18)
    assert mi < 0.05

def test_mi_range():
    from pac_analysis.modulation_index import compute_mi
    rng = np.random.default_rng(7)
    for _ in range(10):
        phase = rng.uniform(-np.pi, np.pi, 500)
        amp = np.abs(rng.normal(1.0, 0.3, 500))
        mi = compute_mi(phase, amp)
        assert 0.0 <= mi <= 1.0

def test_mi_zero_amplitude():
    from pac_analysis.modulation_index import compute_mi
    phase = np.linspace(-np.pi, np.pi, 500)
    amp = np.zeros(500)
    assert compute_mi(phase, amp) == 0.0

def test_mvl_range():
    from pac_analysis.modulation_index import compute_mvl
    rng = np.random.default_rng(3)
    phase = rng.uniform(-np.pi, np.pi, 500)
    amp = np.abs(rng.normal(1.0, 0.3, 500))
    mvl = compute_mvl(phase, amp)
    assert 0.0 <= mvl <= 1.0

def test_mvl_high_for_coupled_signal():
    from pac_analysis.modulation_index import compute_mvl
    fs = 250
    t = np.arange(0, 10.0, 1 / fs)
    phase = (2 * np.pi * 6 * t) % (2 * np.pi) - np.pi
    amp = (np.cos(phase) + 1) / 2
    mvl = compute_mvl(phase, amp)
    assert mvl > 0.1

def test_comodulogram_shape():
    from pac_analysis.modulation_index import comodulogram
    rng = np.random.default_rng(1)
    raw = rng.normal(0, 1, 2500)
    mi_matrix, phase_freqs, amp_freqs = comodulogram(
        raw, fs=250, phase_freqs=(4.0, 12.0, 4.0), amp_freqs=(30.0, 70.0, 20.0),
    )
    assert mi_matrix.shape == (len(phase_freqs), len(amp_freqs))
    assert np.all((mi_matrix >= 0) & (mi_matrix <= 1))


# ── artifact_rejection ──

def test_surrogate_threshold_above_zero():
    from pac_analysis.artifact_rejection import compute_surrogate_threshold
    rng = np.random.default_rng(10)
    phase = rng.uniform(-np.pi, np.pi, 2500)
    amp = np.abs(rng.normal(1.0, 0.2, 2500))
    threshold, surrogates = compute_surrogate_threshold(phase, amp, n_surrogates=50, rng=rng)
    assert threshold > 0.0
    assert len(surrogates) == 50

def test_genuine_pac_passes_surrogate_gate():
    from pac_analysis.modulation_index import compute_mi
    from pac_analysis.artifact_rejection import compute_surrogate_threshold, is_artifactual_pac
    phase_sig, amp_sig = _make_coupled_signals(coupling=0.9)
    mi = compute_mi(phase_sig, amp_sig)
    rng = np.random.default_rng(42)
    threshold, _ = compute_surrogate_threshold(phase_sig, amp_sig, n_surrogates=100, rng=rng)
    genuine, reason = is_artifactual_pac(phase_sig, amp_sig, mi, threshold)
    assert genuine, f"Genuine PAC wrongly rejected: {reason}"

def test_noise_pac_fails_surrogate_gate():
    from pac_analysis.modulation_index import compute_mi
    from pac_analysis.artifact_rejection import compute_surrogate_threshold, is_artifactual_pac
    rng = np.random.default_rng(55)
    phase = rng.uniform(-np.pi, np.pi, 2500)
    amp = np.abs(rng.normal(1.0, 0.1, 2500))
    mi = compute_mi(phase, amp)
    threshold, _ = compute_surrogate_threshold(phase, amp, n_surrogates=100, rng=rng)
    genuine, reason = is_artifactual_pac(phase, amp, mi, threshold)
    assert not genuine

def test_phase_shuffle_threshold():
    from pac_analysis.artifact_rejection import compute_phase_shuffle_null
    rng = np.random.default_rng(7)
    phase = rng.uniform(-np.pi, np.pi, 1000)
    amp = np.abs(rng.normal(1.0, 0.2, 1000))
    threshold, null_dist = compute_phase_shuffle_null(phase, amp, n_shuffles=50, rng=rng)
    assert threshold >= 0.0
    assert len(null_dist) == 50

def test_is_artifactual_below_min_mi():
    from pac_analysis.artifact_rejection import is_artifactual_pac
    rng = np.random.default_rng(0)
    phase = rng.uniform(-np.pi, np.pi, 500)
    amp = rng.uniform(0.5, 1.5, 500)
    genuine, reason = is_artifactual_pac(phase, amp, mi=0.005, surrogate_threshold=0.001, min_mi=0.01)
    assert not genuine
    assert "effect-size floor" in reason


# ── pac_analyzer ──

def test_pac_analyzer_result_keys():
    from pac_analysis.pac_analyzer import PACAnalyzer
    raw = _make_raw_eeg_pac()
    analyzer = PACAnalyzer(fs=250)
    result = analyzer.analyze(raw, rng=np.random.default_rng(0))
    for key in ("mi", "mvl", "is_genuine", "surrogate_threshold", "reason"):
        assert key in result

def test_pac_analyzer_detects_genuine_pac():
    from pac_analysis.pac_analyzer import PACAnalyzer
    raw = _make_raw_eeg_pac(coupling=0.8)
    analyzer = PACAnalyzer(fs=250, n_surrogates=50)
    result = analyzer.analyze(raw, rng=np.random.default_rng(42))
    assert result["mi"] > 0.0

def test_pac_analyzer_mi_in_range():
    from pac_analysis.pac_analyzer import PACAnalyzer
    rng = np.random.default_rng(5)
    raw = rng.normal(0, 1, 2500)
    analyzer = PACAnalyzer(fs=250, n_surrogates=20)
    result = analyzer.analyze(raw, rng=rng)
    assert 0.0 <= result["mi"] <= 1.0

def test_pac_analyzer_default_bands():
    from pac_analysis.pac_analyzer import PACAnalyzer
    a = PACAnalyzer()
    assert a.theta_band == (4.0, 8.0)
    assert a.gamma_band == (30.0, 100.0)


# ── visualization ──

def test_plot_comodulogram_returns_figure():
    import matplotlib
    matplotlib.use("Agg")
    from pac_analysis.visualization import plot_comodulogram
    raw = _make_raw_eeg_pac(coupling=0.7)
    fig = plot_comodulogram(raw, fs=250)
    import matplotlib.pyplot as plt
    assert hasattr(fig, "savefig")
    plt.close("all")
