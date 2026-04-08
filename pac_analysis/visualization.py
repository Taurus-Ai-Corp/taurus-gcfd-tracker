"""PAC visualization: comodulogram heatmap.

Generates publication-standard phase-amplitude coupling figures.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .modulation_index import comodulogram as compute_comodulogram


def plot_comodulogram(
    raw: np.ndarray,
    fs: float,
    title: str = "PAC Comodulogram (Theta-Gamma)",
    phase_freqs: tuple = (2.0, 20.0, 2.0),
    amp_freqs: tuple = (20.0, 100.0, 10.0),
    ax=None,
):
    """Standard PAC comodulogram — MI as function of (phase_freq, amp_freq).

    Hot spot at theta x gamma indicates cross-frequency coupling.
    Required figure for any PAC manuscript submission.

    Returns:
        matplotlib.figure.Figure
    """
    mi_matrix, phase_centers, amp_centers = compute_comodulogram(
        raw, fs, phase_freqs=phase_freqs, amp_freqs=amp_freqs
    )

    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 5))
    else:
        fig = ax.figure

    im = ax.imshow(
        mi_matrix.T,
        origin="lower",
        aspect="auto",
        extent=[phase_centers[0], phase_centers[-1], amp_centers[0], amp_centers[-1]],
        cmap="hot",
        interpolation="bilinear",
    )
    plt.colorbar(im, ax=ax, label="Modulation Index")
    ax.set_xlabel("Phase Frequency (Hz)")
    ax.set_ylabel("Amplitude Frequency (Hz)")
    ax.set_title(title)
    ax.axvline(6, color="white", linestyle="--", alpha=0.7, linewidth=1, label="6 Hz (theta)")
    ax.axhline(40, color="cyan", linestyle="--", alpha=0.7, linewidth=1, label="40 Hz (gamma)")
    ax.legend(fontsize=8, loc="upper right")
    return fig
