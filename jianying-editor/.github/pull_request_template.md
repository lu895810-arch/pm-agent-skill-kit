## Summary

- What changed?
- Why is this needed?

## Scope

- Affected modules/files:
- Breaking changes: yes/no

## Validation

- [ ] `ruff check scripts tests tools`
- [ ] `black --check scripts tests tools`
- [ ] `python -m pytest tests/test_wrapper.py -q`
- [ ] `python tools/check_repo_hygiene.py`
- [ ] `python tools/validate_data_schema.py`

## Risk and Rollback

- Risk level:
- Rollback plan:

## Checklist

- [ ] Docs updated (`SKILL.md` / `rules/` / `docs/api.md`) if API/behavior changed
- [ ] No runtime artifacts committed
