# is_uniq() Implementation Plan

## Gap Analysis

**The gap is ergonomic, not functional.** Users can already do:
```python
df.pipe(verify(~pl.struct("id", "year").is_duplicated()))
```

But `is_uniq()` provides:
- Cleaner syntax: `verify(is_uniq("id", "year"))`
- Better errors: `"is_uniq failed: 3 duplicate(s) in ['id', 'year']"`
- Input validation: Raises if no columns provided
- Discoverability: Autocomplete-friendly API

## Polars Methods Used

| Polars method | What it returns | How checkpl uses it |
|---------------|-----------------|---------------------|
| `pl.col(col).is_duplicated()` | Boolean mask | Single column check |
| `pl.struct(*cols).is_duplicated()` | Boolean mask | Multi-column composite key |
| `.sum()` | Count of True values | Get duplicate count for error message |

---

## Implementation Steps

### Step 1: Implement `is_uniq()` function

**File:** `src/checkpl/predicates/is_uniq.py`

```python
"""Uniqueness check predicate."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import polars as pl

from checkpl.errors import CheckError

if TYPE_CHECKING:
    pass

FrameType = pl.DataFrame | pl.LazyFrame


def is_uniq(*cols: str) -> Callable[[FrameType], FrameType]:
    """Check that column(s) have no duplicate value combinations.

    Args:
        *cols: Column names to check for uniqueness

    Returns:
        A callable that validates the DataFrame and returns it unchanged

    Raises:
        ValueError: If no columns provided
        CheckError: If duplicates found

    Example:
        df.pipe(verify(is_uniq("id")))
        df.pipe(verify(is_uniq("city_id", "year")))
    """
    if not cols:
        raise ValueError("is_uniq() requires at least one column")

    def _check(df: FrameType) -> FrameType:
        # Build expression for duplicate detection
        if len(cols) == 1:
            expr = pl.col(cols[0]).is_duplicated()
        else:
            expr = pl.struct(*cols).is_duplicated()

        # Handle LazyFrame vs DataFrame
        result = df.select(expr.sum())
        if isinstance(result, pl.LazyFrame):
            result = result.collect()
        n_dupes = result.item()

        if n_dupes > 0:
            col_list = list(cols)
            raise CheckError(
                f"is_uniq failed: {n_dupes} duplicate(s) in {col_list}",
                check_name="is_uniq",
            )
        return df

    return _check
```

### Step 2: Export from predicates module

**File:** `src/checkpl/predicates/__init__.py`

```python
"""Predicate functions for column-level checks."""

from checkpl.predicates.is_uniq import is_uniq

__all__ = ["is_uniq"]
```

### Step 3: Export from main package

**File:** `src/checkpl/__init__.py`

Add import and export for `is_uniq`.

### Step 4: Add tests

**File:** `tests/test_checks.py`

Test cases:
- Single column uniqueness (pass)
- Single column duplicates (fail)
- Multi-column composite key (pass)
- Multi-column duplicates (fail)
- Empty DataFrame (pass)
- No columns provided (ValueError)
- Works with verify() wrapper
- Works with LazyFrame
- Error message format
- check_name attribute
- Chained with other verify() calls

---

## Files to Modify

| File | Action |
|------|--------|
| `src/checkpl/predicates/is_uniq.py` | Implement function |
| `src/checkpl/predicates/__init__.py` | Add export |
| `src/checkpl/__init__.py` | Add to public API |
| `tests/test_checks.py` | Add test suite |

---

## Verification

```bash
pytest tests/test_checks.py -v
pytest
```

```python
import polars as pl
from checkpl import verify, is_uniq

df = pl.DataFrame({"id": [1, 2, 3], "year": [2020, 2020, 2021]})
df.pipe(verify(is_uniq("id")))  # pass
df.pipe(verify(is_uniq("id", "year")))  # pass

df2 = pl.DataFrame({"id": [1, 1, 2]})
df2.pipe(verify(is_uniq("id")))  # CheckError
```
