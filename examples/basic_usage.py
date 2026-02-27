"""
Basic usage example for taurus-gcfd-tracker.

Demonstrates:
1. Loading synthetic EEG data
2. Computing the Global Coherence Ratio
3. Interpreting the result
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from taurus_gcfd import CoherenceTracker, datasets


def main():
    # Load simulated MDD patient EEG (10 seconds at 250 Hz)
    print("Loading synthetic EEG data...")
    eeg_data = datasets.load_sample_eeg("patient_01_mdd")
    print(f"  Shape: {eeg_data.shape}, Samples: {len(eeg_data)}")

    # Initialize tracker with standard clinical sampling rate
    tracker = CoherenceTracker(sampling_rate=250)

    # Calculate Global Coherence Ratio
    # Default bands: theta (4-8 Hz) vs gamma (30-100 Hz)
    score = tracker.calculate_global_coherence(eeg_data)

    # Interpret result
    if score >= 0.90:
        status = "HEALTHY"
    elif score >= 0.70:
        status = "MODERATE"
    else:
        status = "LOW"

    print(f"\n  Global Coherence Score: {score:.4f}")
    print(f"  Status: {status}")
    print("  Healthy threshold: >= 0.90")

    # Custom frequency bands (e.g., alpha-gamma coupling)
    alpha_gamma_score = tracker.calculate_global_coherence(
        eeg_data, band1=(8, 13), band2=(30, 100)
    )
    print(f"\n  Alpha-Gamma Coherence: {alpha_gamma_score:.4f}")


if __name__ == "__main__":
    main()
