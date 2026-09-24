# Contributing

## Branching

- Use feature branches for all changes.
- Keep `main` releasable.
- Prefer small, focused pull requests.

## Local Setup

```bash
pip install -r requirements.txt
pip install pytest ruff black pre-commit
pre-commit install
```

## Required Checks

```bash
ruff check scripts tests tools
black --check scripts tests tools
python -m pytest tests/test_wrapper.py -q
python tools/check_repo_hygiene.py
python tools/validate_data_schema.py
```

## Commit Rules

- Use clear commit messages with intent and scope.
- Include docs updates when behavior or APIs change.
- Do not commit runtime artifacts (`cloud_cache`, `__pycache__`, logs).

## Pull Request Rules

- Describe user impact and migration risk.
- Add concrete verification steps.
- Include before/after behavior for API-affecting changes.
