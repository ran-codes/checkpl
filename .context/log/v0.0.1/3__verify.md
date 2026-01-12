# Step 3: Implement verify()

## What verify() Does

`verify()` is the **main entry point** for all validation in checkpl. It accepts either:
- **Polars expressions**: Any expression returning boolean values
  - Operators: `>`, `<`, `==`, `!=`, `>=`, `<=`
  - Boolean: `.is_null()`, `.is_in()`, `.is_between()`, `.is_duplicated()`, etc.
  - String: `.str.contains()`, `.str.starts_with()`, `.str.ends_with()`
  - Temporal: `.dt.is_leap_year()`, or date comparisons with operators
  - List: `.list.contains()`
  - Full boolean reference: [Polars Expressions > Boolean](https://docs.pola.rs/api/python/dev/reference/expressions/boolean.html)
- **Custom predicates**: `verify(is_uniq('id', 'date'))`

```python
# Polars native expressions
df.pipe(verify(pl.col('price') > 0))
df.pipe(verify(pl.col('status').is_in(['A', 'B'])))

# Custom predicates (defined in step 4)
df.pipe(verify(is_uniq('id', 'date')))
df.pipe(verify(not_null('name', 'email')))

# Chaining multiple checks
(
    df
    .pipe(verify(pl.col('x') > 0))
    .pipe(verify(is_uniq('id')))
    .pipe(verify(not_null('name')))
)
```

If validation fails → raises `CheckError`
If passes → returns DataFrame unchanged (for chaining)

---

## Important: Predicates ONLY Work Through verify()

```python
df.pipe(verify(is_uniq('id')))     # ✅ correct
df.pipe(is_uniq('id'))             # ❌ wrong - won't work
```

`verify()` is always required. It's the wrapper that:
1. Takes the DataFrame from `.pipe()`
2. Runs the check (expression or predicate)
3. Returns DataFrame if valid, raises `CheckError` if not

---

## How verify() Works Internally

```
User writes:  df.pipe(verify(something))
                         ↓
              verify(something) returns a function
                         ↓
              .pipe() calls that function with df
                         ↓
              Inside, detect what "something" is:
                ├─ pl.Expr → evaluate, check all True
                └─ callable → call it with df
                         ↓
              Pass → return df | Fail → raise CheckError
```

---

## Implementation

### 3.1 Create `src/checkpl/core/verify.py`

```
IMPORTS:
  - polars
  - CheckError from errors.py
  - typing utilities (Callable, Union, TYPE_CHECKING)

TYPE ALIASES:
  - FrameType = DataFrame or LazyFrame
  - CheckType = Polars Expr or Callable

HELPER FUNCTION _to_scalar(result):
  - If result is LazyFrame → collect it first
  - Extract single value using .item()
  - Return the scalar value

FUNCTION verify(check) → returns a function:
  """
  Main entry point for all validation.
  Accepts: Polars expression OR callable predicate
  Returns: function that validates DataFrame
  """

  INNER FUNCTION _verify(df):
    IF check is a Polars expression:
      - Count rows where expression is False: (~check).sum()
      - If any failures → raise CheckError with count
      - Otherwise → return df unchanged

    ELSE IF check is callable:
      - Call it with df: check(df)
      - Return whatever it returns (predicate handles its own errors)

    ELSE:
      - raise TypeError (invalid input type)

  RETURN _verify
```

### Logic Summary

| Step | What Happens |
|------|--------------|
| 1. Detect type | Is it `pl.Expr` or `callable`? |
| 2a. Expression path | Negate expression, sum False values, raise if > 0 |
| 2b. Callable path | Just call it with df (predicate handles errors) |
| 3. Return | df unchanged if valid |

### Why This Design?

1. **Single entry point** - All validation goes through `verify()`
2. **Flexible** - Works with native Polars syntax AND custom predicates
3. **Consistent** - Same pattern for everything: `df.pipe(verify(...))`
4. **Extensible** - Easy to add new predicates later

---

### 3.2 Update `src/checkpl/core/__init__.py`

```
- Import hello from hello.py
- Import verify from verify.py
- Export both in __all__
```

---

### 3.3 Update `src/checkpl/__init__.py`

```
- Import hello, verify from core
- Import CheckError from errors
- Set __version__ = "0.0.1"
- Export: hello, verify, CheckError, __version__
```

---

## 4. Tests (pytest)

**Note:** At this stage, we only test Polars native expressions. Predicate/callable tests come in step 4.

Create `tests/test_verify.py`:

```
CLASS TestVerifyExpressions:
  """Basic pass/fail behavior with Polars expressions."""

  - test_passes_when_all_rows_true
      → df with [1,2,3], verify(col > 0) → returns df unchanged

  - test_fails_when_some_rows_false
      → df with [1,-1,3], verify(col > 0) → raises CheckError, match "1 row"

  - test_fails_reports_correct_count
      → df with [-1,-2,3], verify(col > 0) → raises CheckError, match "2 row"

  - test_check_name_is_verify
      → on failure, CheckError.check_name == "verify"


CLASS TestVerifyPolarsExpressionTypes:
  """Verify works with different Polars expression types."""

  - test_comparison_greater_than    → col > value
  - test_comparison_less_than       → col < value
  - test_comparison_equals          → col == value
  - test_is_in_expression           → col.is_in([...])
  - test_is_between_expression      → col.is_between(low, high)
  - test_is_not_null_expression     → col.is_not_null()
  - test_str_len_expression         → col.str.len_chars() > 0


CLASS TestVerifyDataFrameTypes:
  """DataFrame and LazyFrame support."""

  - test_works_with_dataframe
      → Input DataFrame → returns DataFrame

  - test_works_with_lazyframe
      → Input LazyFrame → returns LazyFrame

  - test_returns_same_type_as_input
      → Output type matches input type


CLASS TestVerifyEdgeCases:
  """Edge cases and boundary conditions."""

  - test_empty_dataframe_passes
      → Empty df passes (no rows to fail)

  - test_single_row_passes
      → Single valid row works

  - test_single_row_fails
      → Single invalid row raises error

  - test_all_rows_fail
      → All rows failing shows correct count

  - test_nulls_in_expression_column
      → Nulls are skipped in sum (pass by default)
      → Note: Consider special null handling in future

  - test_multiple_columns_in_expression
      → Expression can compare col("a") > col("b")

  - test_chaining_multiple_verifies
      → Can chain: df.pipe(verify(...)).pipe(verify(...))
```

Run tests:
```bash
uv run pytest tests/test_verify.py -v
```

---

## 5. Scratch Script (Quick Testing)

Create `.context/log/v0.0.1/3__verify.py`:

```
IMPORTS: polars, verify, CheckError

TEST 1: Expression passes
  - Create df with positive values
  - verify(col > 0) should pass
  - Print success

TEST 2: Expression fails
  - Create df with some negative values
  - verify(col > 0) should raise CheckError
  - Catch and print error message + check_name

TEST 3: LazyFrame support
  - Create LazyFrame
  - verify() should return LazyFrame
  - Print type to confirm

TEST 4: Complex expression
  - Create df with status column
  - verify(col.is_in([...])) should pass

TEST 5: Callable predicate (mock)
  - Define simple function that returns df
  - verify(mock_function) should call it
  - Confirms callable path works

TEST 6: Invalid type
  - verify("string") should raise TypeError
  - Catch and print error

PRINT "All tests passed!"
```

Run:
```bash
uv run python .context/log/v0.0.1/3__verify.py
```

---

## Checklist

- [ ] Updated `src/checkpl/core/verify.py` with new `verify()` that handles expressions AND callables
- [ ] Updated `src/checkpl/core/__init__.py` to export `verify`
- [ ] Updated `src/checkpl/__init__.py` to export `verify`
- [ ] Created test script and verified it works

---

## Next Step

Once verified, proceed to `4__predicates.md` to implement `is_uniq()` and `not_null()` predicates that return callables for `verify()` to use.
