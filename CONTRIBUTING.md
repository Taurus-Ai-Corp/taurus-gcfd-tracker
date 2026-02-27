# Contributing to taurus-gcfd-tracker

Thank you for your interest in contributing.

## How to Contribute

1. **Fork** the repository
2. **Create a branch** (`git checkout -b feature/your-feature`)
3. **Make changes** and ensure they pass lint and tests
4. **Commit** with a descriptive message
5. **Push** to your fork and open a **Pull Request**

## Development Setup

```bash
git clone https://github.com/YOUR-USERNAME/taurus-gcfd-tracker.git
cd taurus-gcfd-tracker
pip install numpy scipy matplotlib ruff pytest
```

## Code Standards

- Python 3.9+ compatibility
- Lint with `ruff check .`
- No proprietary terms (the IP guard hook will block commits containing them)

## What We Welcome

- Additional frequency band presets (alpha-beta, delta-theta, etc.)
- Dataset integrations (EEGLAB, MNE-Python, BrainDecode)
- Performance optimizations (GPU acceleration, streaming)
- Clinical validation case studies
- Documentation improvements

## What We Cannot Accept

- Code containing proprietary algorithms or trade secrets
- Dependencies on non-open-source libraries
- Changes that break the Apache 2.0 license compatibility

## IP Guard

This repository uses a pre-commit hook (`tools/ip_guard_hook.sh`) that blocks
commits containing proprietary terms. If your commit is rejected, review your
changes for any blocked patterns and remove them.

## Code of Conduct

All contributors must follow our [Code of Conduct](CODE_OF_CONDUCT.md).
