# Step 2: Implement errors.py

## Why errors.py is First (After Setup)

**Dependency order.** Code must be implemented in the order it's needed:

```
errors.py       ← depends on nothing (implement first)
    ↓
verify.py       ← imports CheckError from errors.py
is_uniq.py      ← imports CheckError from errors.py
not_null.py     ← imports CheckError from errors.py
    ↓
__init__.py     ← imports from all the above
    ↓
tests           ← imports from __init__.py
```

If you wrote `verify.py` first with `raise CheckError(...)`, you'd get an import error because `CheckError` wouldn't exist yet.

---

## What errors.py Does

It defines a **custom exception class** that all checkpl functions raise when validation fails. It iwll give a custom error linked to `checkpl` which allow suers to easily understand where error happned instead of a generic "Exception" error.

### Why Not Use Built-in Exceptions?

| Option | Problem |
|--------|---------|
| `ValueError` | Too generic. `except ValueError` catches ALL ValueErrors, not just yours. |
| `AssertionError` | Convention is for "this should never happen" bugs, not data validation. |
| `CheckError` (custom) | Users can catch specifically: `except CheckError`. Professional. |

### How Developers Use It (Primary Use)

**This is the main purpose.** We import `CheckError` into our predicate files and raise it when validation fails.

Example: inside `src/checkpl/predicates/is_uniq.py`:

```python
from assert_polarserrors import CheckError  # ← import it

def is_uniq(*cols: str):
    def _check(df):
        # ... validation logic ...

        if duplicates_found:
            raise CheckError(                          # ← raise it
                f"is_uniq failed: {count} duplicate(s) in {cols}",
                check_name="is_uniq",                  # ← identify which check
            )
        return df
    return _check
```

Every predicate file (`is_uniq.py`, `not_null.py`, `verify.py`) will follow this pattern:
1. Import `CheckError` from `assert_polarserrors`
2. Raise it with a message and `check_name` when validation fails

### How End Users *Might* Use It (Rare)

**Note:** Most users will NOT catch the error. They'll just let it crash - that's the whole point of validation! If data is bad, stop the pipeline.

```python
# Typical usage - no try/except, just let it crash if invalid
df.pipe(is_uniq('id')).pipe(not_null('name'))
```

But *some* users might want to catch and handle errors gracefully:

```python
from checkpl import is_uniq, CheckError

try:
    df.pipe(is_uniq('id'))
except CheckError as e:
    print(f"Validation failed: {e}")
    print(f"Which check: {e.check_name}")  # "is_uniq"
    # maybe log it, send alert, use fallback data, etc.
```

The `check_name` attribute lets them identify *which* check failed programmatically.

---

## Implementation

### 2.1 Update `src/checkpl/errors.py`

Replace the contents with:

```python
"""Custom exceptions for assert_polars"""


class CheckError(Exception):
    """Raised when a data validation check fails.

    Attributes:
        check_name: Name of the check that failed (e.g., "is_uniq", "not_null")

    Example:
        try:
            df.pipe(is_uniq('id'))
        except CheckError as e:
            print(f"Check '{e.check_name}' failed: {e}")
    """

    def __init__(self, message: str, check_name: str | None = None):
        super().__init__(message)
        self.check_name = check_name
```

#### Code Breakdown

| Line | What It Does |
|------|--------------|
| `class CheckError(Exception):` | Creates a new exception type that inherits from Python's base `Exception` |
| `def __init__(self, message, check_name=None):` | Constructor takes a message and optional check name |
| `super().__init__(message)` | Passes message to parent `Exception` class (so `str(e)` works) |
| `self.check_name = check_name` | Stores which check failed as an attribute |

#### Why `str | None` Type Hint?

```python
check_name: str | None = None
```

- `str | None` means "either a string or None" (Python 3.10+ syntax)
- `= None` makes it optional (defaults to None if not provided)
- This allows: `CheckError("failed")` or `CheckError("failed", check_name="is_uniq")`

---

### 2.2 Verify It Works

After implementing, test in terminal:

```bash
uv run python -c "
from assert_polarserrors import CheckError

# Test creating an error
e = CheckError('test message', check_name='is_uniq')
print(f'Message: {e}')
print(f'Check name: {e.check_name}')

# Test raising and catching
try:
    raise CheckError('validation failed', check_name='not_null')
except CheckError as caught:
    print(f'Caught: {caught.check_name}')
"
```

Expected output:
```
Message: test message
Check name: is_uniq
Caught: not_null
```

---

## Checklist

- [ ] Updated `src/checkpl/errors.py` with `CheckError` class
- [ ] Verified with test command above

---

## Next Step

Once verified, proceed to `3__verify.md` to implement the `verify()` function.
