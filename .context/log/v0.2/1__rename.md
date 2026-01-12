# Step 6: Rename Package (checkpl → assert-polars)

This guide covers renaming the package from `checkpl` to `assert-polars`.

---

## 6.1 Naming Convention

**Python package naming:**
- PyPI package names can have hyphens, underscores, or dots (case-insensitive, normalized)
- Python import names must be valid identifiers (no hyphens allowed)

**Our naming decision:**
| Context | Name |
|---------|------|
| PyPI package | `assert-polars` |
| Python import | `assert_polars` |
| Source directory | `src/assert_polars/` |
| GitHub repo | `ran-codes/assert-polars` |

Users will run:
```bash
pip install assert-polars
```

And import:
```python
from assert_polars import verify, is_uniq
```

---

## 6.2 Version Reset

Starting fresh with `0.1.0` since this is effectively a new package on PyPI.

The old `checkpl` package (v0.1.1) will remain on PyPI but won't be updated.

---

## 6.3 Changes Required

### Step 1: Rename Source Directory
```bash
mv src/checkpl src/assert_polars
```

### Step 2: Update pyproject.toml
- `name = "checkpl"` → `name = "assert-polars"`
- `version = "0.1.1"` → `version = "0.1.0"`
- Update GitHub URLs to `ran-codes/assert-polars`

### Step 3: Update Source File Imports
All internal imports change from `checkpl` to `assert_polars`:

| File | Changes |
|------|---------|
| `src/assert_polars/__init__.py` | 3 imports + docstring |
| `src/assert_polars/core/__init__.py` | 2 imports |
| `src/assert_polars/core/verify.py` | 1 import + docstring |
| `src/assert_polars/core/hello.py` | docstring + return string |
| `src/assert_polars/errors.py` | docstring |
| `src/assert_polars/predicates/__init__.py` | 1 import |
| `src/assert_polars/predicates/is_uniq.py` | 1 import |

### Step 4: Update Test Files
| File | Changes |
|------|---------|
| `tests/test_verify.py` | import line |
| `tests/test_predicate_is_uniq.py` | import line |
| `tests/test_checks.py` | docstring |

### Step 5: Update README.md
- Title: `# checkpl` → `# assert-polars`
- Install: `pip install checkpl` → `pip install assert-polars`
- Imports: `from assert_polars import` → `from assert_polars import`

### Step 6: Regenerate uv.lock
```bash
uv lock
```

---

## 6.4 Verification

```bash
# Reinstall with new name
uv sync

# Test import works
uv run python -c "from assert_polars import verify, is_uniq; print('OK')"

# Run tests
uv run pytest
```

---

## 6.5 Checklist

- [ ] Renamed `src/checkpl/` → `src/assert_polars/`
- [ ] Updated `pyproject.toml` (name, version, URLs)
- [ ] Updated all source file imports
- [ ] Updated test file imports
- [ ] Updated README.md
- [ ] Ran `uv lock`
- [ ] Verified `uv sync` works
- [ ] Verified import works
- [ ] Verified tests pass
- [ ] Renamed GitHub repo to `assert-polars`
