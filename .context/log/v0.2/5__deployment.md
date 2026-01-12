# checkpl Release Plan

## Goal

Publish checkpl to PyPI so it's installable via:
- `pip install checkpl`
- `micropip.install("checkpl")` (Pyodide/Marimo)

**Why micropip works:** checkpl is pure Python (`py3-none-any.whl`), so micropip can install it directly from PyPI. Polars has WASM builds for Pyodide.

---

## 1. Pre-flight

### 1.1 Run Tests
```bash
uv run pytest -v
```

### 1.2 Update pyproject.toml Metadata

Current gaps:
- Description is placeholder
- Missing: license, keywords, classifiers, project URLs

**Updated pyproject.toml:**

```toml
[project]
name = "checkpl"
version = "0.1.0"
description = "Simple inline data validation for Polars DataFrames"
readme = "README.md"
license = "MIT"
authors = [
    { name = "ran li", email = "ranli2011@gmail.com" }
]
requires-python = ">=3.12"
keywords = ["polars", "validation", "data-quality", "dataframe"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering",
]
dependencies = [
    "polars>=1.37.0",
]

[project.urls]
Homepage = "https://github.com/YOUR_USER/checkpl"
Repository = "https://github.com/YOUR_USER/checkpl"

[build-system]
requires = ["uv_build>=0.8.22,<0.9.0"]
build-backend = "uv_build"

[dependency-groups]
dev = [
    "pytest>=9.0.2",
    "ruff>=0.14.11",
]
```

### 1.3 Review README.md

Ensure it's user-facing (shown on PyPI page).

---

## 2. Build

```bash
uv build
```

Output:
- `dist/checkpl-0.1.0-py3-none-any.whl`
- `dist/checkpl-0.1.0.tar.gz`

---

## 3. Publish

```bash
uv publish
```

Or with explicit token:
```bash
uv publish --token pypi-xxxx
```

---

## 4. Verification

### 4.1 Standard pip install
```bash
pip install checkpl
```

### 4.2 Pyodide/Marimo test
```python
import micropip
await micropip.install("checkpl")
from checkpl import verify, is_uniq
```

---

## Files to Update

| File | Changes |
|------|---------|
| `pyproject.toml` | Add description, license, classifiers, URLs |
| `README.md` | Ensure it's user-facing |

---

## Steps Summary

1. [ ] Run tests: `uv run pytest -v`
2. [ ] Update `pyproject.toml` metadata
3. [ ] Review `README.md`
4. [ ] Build: `uv build`
5. [ ] Publish: `uv publish`
6. [ ] Verify: `pip install checkpl`


# Marimo Example Code

```python
import polars as pl
from checkpl import verify, is_uniq

# Should pass
df_good = pl.DataFrame({
    "id": [1, 2, 3, 4],
    "name": ["Alice", "Bob", "Charlie", "Diana"],
    "amount": [100.0, 250.5, 75.0, 300.0],
    "year": [2020, 2021, 2022, 2023],
})

(
    df_good
    .pipe(verify(pl.col("amount") > 0))           # all amounts positive
    .pipe(verify(pl.col("name").str.len_chars() > 0))  # names not empty
    .pipe(verify(is_uniq("id")))                  # single column uniqueness
    .pipe(verify(is_uniq("name", "year")))        # compound uniqueness
)

# Should fail
df_bad = pl.DataFrame({
    "id": [1, 1, 2],                   # duplicate id=1
    "name": ["Alice", "Bob", "Charlie"],
    "amount": [100.0, -50.0, 200.0],   # -50 violates amount > 0
})

(
    df_bad
    .pipe(verify(is_uniq("id")))
)

```


