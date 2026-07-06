# Contributing to ScatterBootstrap

Thanks for your interest in improving ScatterBootstrap! Contributions of all
kinds are welcome: bug reports, documentation, new scattering models, and code.

## Getting help / asking questions

- **Questions and usage help**: open a [GitHub Discussion][discussions] or a
  question-labelled issue.
- **Bug reports**: open a [GitHub issue][issues] and include:
  - your OS, Python version, and how you installed the package;
  - a minimal script that reproduces the problem;
  - the full traceback or incorrect output you observed.
- **Feature requests**: open an issue describing the use case and, if possible,
  the scattering model or workflow you have in mind.

## Development setup

ScatterBootstrap contains C extensions, so you need a C compiler (GCC, Clang, or
MSVC — see the README for platform details). Then:

```bash
git clone https://github.com/TobiasMKaufmann/ScatterBootstrap.git
cd ScatterBootstrap
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -e .[dev]
```

`pip install -e .` compiles `libsas_core` and all model extensions in place.

## Running the tests

```bash
pytest                      # full suite
pytest --cov=scatterbootstrap   # with coverage
```

Please add or update tests for any change in behaviour. Every bundled model is
covered by a parametrized smoke test in `tests/`; new models must be added to the
parameter fixtures in `tests/conftest.py`.

## Code style

- Format with `black` (line length 88) and keep `flake8` clean.
- Use NumPy-style docstrings for public functions.

```bash
black src/scatterbootstrap tests
flake8 src/scatterbootstrap tests --max-line-length=100 --extend-ignore=E203,W503
```

## Adding a new scattering model

1. Create `src/scatterbootstrap/form_factors/<name>/` (or `structure_factors/`)
   containing `<name>.c`, `<name>.h`, `wrapper.py`, and `__init__.py`.
2. The C kernel should expose `Fq(...)` (form factors) or `Iq(...)`
   (structure factors); reuse the shared helpers in `scatterbootstrap/lib`.
3. `wrapper.py` must define `compute_form_factor(q, **params)` (or
   `compute_structure_factor`). Use `scatterbootstrap._lib_finder.find_library`
   to locate the compiled binary.
4. Rebuild with `pip install -e .` — the model is auto-discovered, compiled, and
   exposed by name.
5. Add a representative parameter set to `tests/conftest.py`.

See `EXAMPLE_ADDING_NEW_MODEL.md` for a worked example.

## Pull requests

1. Fork the repository and create a feature branch.
2. Make your change with tests and documentation.
3. Ensure `pytest`, `black --check`, and `flake8` pass.
4. Open a pull request describing the motivation and the change.

By contributing you agree that your contributions are licensed under the MIT
License (with model kernels adapted from SasView remaining under their original
BSD-3-Clause license). All participants are expected to follow our
[Code of Conduct](CODE_OF_CONDUCT.md).

[issues]: https://github.com/TobiasMKaufmann/ScatterBootstrap/issues
[discussions]: https://github.com/TobiasMKaufmann/ScatterBootstrap/discussions
