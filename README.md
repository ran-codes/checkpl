# checkpl

Ergonomic inline validation for Polars DataFrames.

## Installation

```bash
pip install checkpl
```

## Quick Start

```python
import polars as pl
from assert_polars import verify, is_uniq

df = pl.DataFrame({
    "id": [1, 2, 3],
    "city": ["NYC", "LA", "NYC"],
    "year": [2020, 2020, 2021]
})

# Validate with Polars expressions
df.pipe(verify(pl.col("year") >= 2020))

# Validate uniqueness
df.pipe(verify(is_uniq("id")))

# Composite key uniqueness
df.pipe(verify(is_uniq("city", "year")))

# Chain validations
(
    df
    .pipe(verify(pl.col("year") >= 2020))
    .pipe(verify(is_uniq("id")))
    .filter(pl.col("city") == "NYC")
)
```

## Features

- **Pipeable**: Integrates with Polars' `.pipe()` for fluent data pipelines
- **Native expressions**: Use any Polars boolean expression directly
- **Predicates**: Built-in checks like `is_uniq()` for common validations
- **Clear errors**: `CheckError` with descriptive messages and failure counts
- **LazyFrame support**: Works with both `DataFrame` and `LazyFrame`

## API

### `verify(check)`

Validate a DataFrame using a Polars expression or predicate.

```python
# With Polars expression
df.pipe(verify(pl.col("price") > 0))

# With predicate
df.pipe(verify(is_uniq("id")))
```

Raises `CheckError` if validation fails, returns DataFrame unchanged if valid.

### `is_uniq(*cols)`

Check that column(s) have no duplicate values.

```python
df.pipe(verify(is_uniq("id")))           # Single column
df.pipe(verify(is_uniq("id", "year")))   # Composite key
```

## Error Handling

```python
from assert_polars import CheckError

try:
    df.pipe(verify(is_uniq("id")))
except CheckError as e:
    print(f"Check '{e.check_name}' failed: {e}")
```

## License

MIT
