# Custom Checks

veritail includes a set of built-in deterministic checks (zero results, price outliers, near-duplicates, etc.). When you need domain-specific quality checks, you can add your own without modifying veritail itself by providing a custom check module.

## Check Function Signature

A check module is a Python file containing one or more functions whose names start with `check_`. Each function must accept a `QueryEntry` and a `list[SearchResult]`, and return a `list[CheckResult]`:

```python
def check_<name>(query: QueryEntry, results: list[SearchResult]) -> list[CheckResult]:
    ...
```

All three types are importable from `veritail.types`:

```python
from veritail.types import CheckResult, QueryEntry, SearchResult
```

## Example: Species Mismatch Check

```python
# my_checks.py
from veritail.types import CheckResult, QueryEntry, SearchResult


def check_species_mismatch(
    query: QueryEntry, results: list[SearchResult]
) -> list[CheckResult]:
    """Flag cross-species results in pet supply searches."""
    checks = []
    for r in results:
        species = r.attributes.get("species")
        if species and species.lower() not in query.query.lower():
            checks.append(
                CheckResult(
                    check_name="species_mismatch",
                    query=query.query,
                    product_id=r.product_id,
                    passed=False,
                    detail=f"Query mentions no '{species}' but result is for {species}",
                )
            )
    return checks
```

## Naming Conventions

- **`check_*` callable functions** are discovered and run automatically.
- **Non-callable names** starting with `check_` (e.g., `check_threshold = 0.5`) are silently skipped. This lets you define constants alongside your check functions without triggering errors.
- **Helper functions** without the `check_` prefix are ignored by the loader. Use any prefix other than `check_` for utility functions.

If a module contains no callable `check_*` functions, veritail raises an error at startup.

## Usage

Pass one or more `--checks` flags to `veritail run`. Each flag points to a Python file:

```bash
veritail run \
  --queries queries.csv \
  --adapter my_adapter.py \
  --checks my_checks.py \
  --checks more_checks.py \
  --llm-model gpt-4o
```

Custom check results appear alongside built-in checks in both the terminal output and the HTML report.

See the [CLI Reference](cli-reference.md) for the full list of `veritail run` options.
