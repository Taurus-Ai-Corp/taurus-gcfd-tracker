"""Phase-Amplitude Coupling analysis module.

Implements Tort Modulation Index (Tort et al. 2010) with 4-stage artifact
rejection addressing Aru et al. (2015) criticisms of spurious PAC in
consumer-grade EEG.

References:
  Tort et al. (2010). J Neurophysiol 104:1195-1210.
  Canolty et al. (2006). Science 313:1626-1628.
  Cohen (2008). J Neurosci Methods 168:494-499.
  Aru et al. (2015). Curr Opin Neurobiol 31:51-61.
"""
from .modulation_index import compute_mi, compute_mvl, comodulogram
from .artifact_rejection import (
    compute_surrogate_threshold,
    compute_phase_shuffle_null,
    is_artifactual_pac,
)
from .pac_analyzer import PACAnalyzer
from .visualization import plot_comodulogram

__all__ = [
    "compute_mi",
    "compute_mvl",
    "comodulogram",
    "compute_surrogate_threshold",
    "compute_phase_shuffle_null",
    "is_artifactual_pac",
    "PACAnalyzer",
    "plot_comodulogram",
]
