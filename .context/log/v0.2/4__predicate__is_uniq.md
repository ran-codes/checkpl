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

## 1. Implementation Steps

### 1.1: Implement `is_uniq()` function

**File:** `src/checkpl/predicates/is_uniq.py`

```python
"""Uniqueness check predicate."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import polars as pl

from assert_polarserrors import CheckError

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

### 1.2: Export from predicates module

**File:** `src/checkpl/predicates/__init__.py`

```python
"""Predicate functions for column-level checks."""

from assert_polarspredicates.is_uniq import is_uniq

__all__ = ["is_uniq"]
```

### 1.3: Export from main package

**File:** `src/checkpl/__init__.py`

Add import and export for `is_uniq`.

### 1.4: Add tests

**File:** `tests/test_predicate_is_uniq.py`

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
| `tests/test_predicate_is_uniq.py` | Add test suite |

---

## 2. Test

**File:** `tests/test_predicate_is_uniq.py`

```python
"""Tests for predicate functions."""

import polars as pl
import pytest

from assert_polars import verify, is_uniq, CheckError


class TestIsUniq:
    """Tests for is_uniq() predicate."""

    # --- Passing cases ---

    def test_single_column_unique_passes(self):
        """All values unique in single column."""
        df = pl.DataFrame({"id": [1, 2, 3]})
        result = df.pipe(verify(is_uniq("id")))
        assert result.equals(df)

    def test_multi_column_unique_passes(self):
        """Composite key is unique."""
        df = pl.DataFrame({
            "city_id": [1, 1, 2],
            "year": [2020, 2021, 2020]
        })
        result = df.pipe(verify(is_uniq("city_id", "year")))
        assert result.equals(df)

    def test_empty_dataframe_passes(self):
        """Empty DataFrame has no duplicates."""
        df = pl.DataFrame({"id": []}).cast({"id": pl.Int64})
        result = df.pipe(verify(is_uniq("id")))
        assert result.equals(df)

    # --- Failing cases ---

    def test_single_column_duplicates_fails(self):
        """Duplicates in single column raises CheckError."""
        df = pl.DataFrame({"id": [1, 1, 2]})
        with pytest.raises(CheckError, match="2 duplicate"):
            df.pipe(verify(is_uniq("id")))

    def test_multi_column_duplicates_fails(self):
        """Duplicate composite key raises CheckError."""
        df = pl.DataFrame({
            "city_id": [1, 1, 2],
            "year": [2020, 2020, 2021]
        })
        with pytest.raises(CheckError, match="2 duplicate"):
            df.pipe(verify(is_uniq("city_id", "year")))

    # --- Error attributes ---

    def test_check_name_is_is_uniq(self):
        """CheckError has check_name='is_uniq'."""
        df = pl.DataFrame({"id": [1, 1]})
        with pytest.raises(CheckError) as exc_info:
            df.pipe(verify(is_uniq("id")))
        assert exc_info.value.check_name == "is_uniq"

    def test_error_message_contains_columns(self):
        """Error message lists the columns checked."""
        df = pl.DataFrame({"a": [1, 1], "b": [2, 2]})
        with pytest.raises(CheckError, match=r"\['a', 'b'\]"):
            df.pipe(verify(is_uniq("a", "b")))

    # --- Input validation ---

    def test_no_columns_raises_valueerror(self):
        """Calling is_uniq() with no columns raises ValueError."""
        with pytest.raises(ValueError, match="at least one column"):
            is_uniq()

    # --- LazyFrame support ---

    def test_works_with_lazyframe(self):
        """Returns LazyFrame when given LazyFrame."""
        lf = pl.LazyFrame({"id": [1, 2, 3]})
        result = lf.pipe(verify(is_uniq("id")))
        assert isinstance(result, pl.LazyFrame)

    # --- Chaining ---

    def test_chaining_with_other_checks(self):
        """Can chain is_uniq with other verify calls."""
        df = pl.DataFrame({"id": [1, 2, 3], "val": [10, 20, 30]})
        result = (
            df
            .pipe(verify(is_uniq("id")))
            .pipe(verify(pl.col("val") > 0))
        )
        assert result.equals(df)
```

---

## 3. Interactive Test

```bash
pytest tests/test_predicate_is_uniq.py -v
```

```python
import polars as pl
from assert_polars import verify, is_uniq

# --- Should pass ---
df = pl.DataFrame({"id": [1, 2, 3], "year": [2020, 2020, 2021]})
df.pipe(verify(is_uniq("id")))           # unique ids
df.pipe(verify(is_uniq("id", "year")))   # unique composite key

# --- Should fail ---
df2 = pl.DataFrame({"id": [1, 1, 2]})
df2.pipe(verify(is_uniq("id")))          # CheckError: 2 duplicate(s) in ['id']

# --- Should raise ValueError ---
is_uniq()  # ValueError: is_uniq() requires at least one column
```
