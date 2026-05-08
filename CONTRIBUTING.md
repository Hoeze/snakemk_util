# Contributing to `snakemk_util`

## Development environment

The project uses [`uv`](https://docs.astral.sh/uv/) for dependency management.

### Initial setup

```bash
# Create the conda env (provides Python + uv)
micromamba env create -f environment-dev.yml
micromamba activate snakemk_util

# Install all dependency groups (runtime + dev + test + lint) into a uv-managed venv
uv sync --all-groups --all-extras
```

All subsequent commands assume the env is activated and `uv` is on `PATH`.

## Running tasks

The project standardises tasks through [`tox`](https://tox.wiki/) with the `tox-uv` runner. Run any environment with:

```bash
uv run tox -e <env>
```

Available environments (defined in `pyproject.toml`):

| Env             | Purpose                                  |
|-----------------|------------------------------------------|
| `format-check`  | `ruff format --check .`                  |
| `lints`         | `ruff check .`                           |
| `typecheck`     | `mypy snakemk_util`                      |
| `py3.11`        | Run pytest under Python 3.11             |
| `py3.14`        | Run pytest under Python 3.14             |

Run the full matrix CI runs with:

```bash
uv run tox
```

### Quick commands

```bash
# Format code
uv run ruff format .

# Lint with autofix
uv run ruff check --fix .

# Run tests directly (single Python)
uv run pytest

# Run a single test
uv run pytest tests/test_rule_args.py::test_name -x
```

## Releases

Versioning and tagging are automated by [release-please](https://github.com/googleapis/release-please) (`.github/workflows/release-please.yml`). Publishing is handled by `.github/workflows/publish.yml`:

- release-please watches commits on `master` and opens/maintains a release PR that bumps `pyproject.toml` and updates `CHANGELOG.md`.
- Merging the release PR cuts a `vX.Y.Z` tag and a GitHub release.
- The tag triggers `publish.yml`, which builds sdist + wheel and uploads to PyPI via trusted publishing (OIDC).
- `__version__` is sourced at runtime from package metadata (`importlib.metadata.version("snakemk_util")`).

Use [Conventional Commits](https://www.conventionalcommits.org/) on `master` so release-please can pick the next version (`fix:` → patch, `feat:` → minor, `feat!:` / `BREAKING CHANGE:` → major).

