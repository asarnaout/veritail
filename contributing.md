# Contributing

Thanks for contributing to veritail.

## Before you start

- Open an issue first for large feature work or behavior changes.
- Use a feature branch for all changes; do not work directly on `main`.
- Keep pull requests focused and scoped to a single problem.

## Development setup

```bash
git clone https://github.com/asarnaout/veritail.git
cd veritail
pip install -e ".[dev,cloud]"
```

Python 3.9+ is required.

## Branching, commits, and PR flow

Create a feature branch from an up-to-date `main`:

```bash
git checkout main
git pull origin main
git checkout -b feature/short-description
```

Commit frequently in small, logical chunks:

```bash
git add <files>
git commit -m "Short description of change"
```

Push your feature branch and open a PR to `main`:

```bash
git push -u origin feature/short-description
```

If `main` has moved while you are working, re-sync before final review:

```bash
git fetch origin
git rebase origin/main
git push --force-with-lease
```

## Required checks

Run these before opening a pull request:

```bash
pytest
ruff check src tests
mypy src
```

## Code and tests

- Add or update tests for any behavior change.
- Keep type annotations and `mypy` strict-mode compatibility.
- Reuse existing patterns in `src/veritail/` and avoid unrelated refactors.

## Documentation updates

Update docs when you change user-facing behavior:

- `README.md` for quick-start or CLI examples
- `docs/cli-reference.md` for flags and command behavior
- `CHANGELOG.md` for notable updates (when applicable)

## Pull request checklist

- [ ] Branch created from `main` and PR targets `main`
- [ ] Small, frequent commits with clear commit messages
- [ ] Tests added/updated and passing locally
- [ ] `ruff`, `mypy`, and `pytest` pass
- [ ] Documentation updated for any user-visible change
- [ ] No generated outputs committed (`eval-results/`, local scratch files)
