# Step 1: Project & Package Setup

This guide covers the boilerplate setup - no actual checkpl logic yet.

---

## 1.1 Initialize Project with uv

You already ran this:
```bash
uv init --lib
```

**What it created:**
- `pyproject.toml` - package configuration
- `src/checkpl/__init__.py` - package entry point
- `src/checkpl/py.typed` - marker for type checkers
- `.python-version` - pins Python version

---

## 1.2 Add Dependencies

**Add polars (runtime dependency):**
```bash
uv add polars
```

**Add dev dependencies (not installed by end users):**
```bash
uv add --dev pytest ruff
```

**What happens:**
- `pyproject.toml` gets updated with dependencies
- `uv.lock` is created/updated (lockfile for reproducible installs)
- A `.venv/` folder is created with your virtual environment

---

## 1.3 Create Directories

```bash
mkdir tests
```

**Your structure should now look like:**
```
checkpl/
├── .venv/               # created by uv
├── src/
│   └── checkpl/
│       ├── __init__.py  # created by uv init
│       └── py.typed     # created by uv init
├── tests/               # you just created this
├── .python-version
├── pyproject.toml
├── uv.lock
└── README.md
```

---

## 1.4 Configure pyproject.toml

Open `pyproject.toml` and replace its contents with:

```toml
[project]
name = "checkpl"
version = "0.0.1"
description = "Simple inline data validation for Polars"
readme = "README.md"
requires-python = ">=3.10"
dependencies = ["polars>=1.0"]

[dependency-groups]
dev = ["pytest", "ruff"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/checkpl"]

[tool.ruff]
line-length = 88
target-version = "py310"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

**What each section does:**

| Section | Purpose |
|---------|---------|
| `[project]` | Package metadata (name, version, description) |
| `requires-python` | Minimum Python version |
| `dependencies` | What gets installed when users `pip install checkpl` |
| `[dependency-groups]` | Dev-only tools (pytest, ruff) |
| `[build-system]` | How to build the package (hatchling is modern & simple) |
| `[tool.hatch.build...]` | Tells hatch where your source code lives |
| `[tool.ruff]` | Linter settings |
| `[tool.pytest...]` | Test runner settings |

---

## 1.5 Create Empty Package Files

**Create `src/checkpl/errors.py`:**
```python
"""Custom exceptions for checkpl."""
```

**Create `src/checkpl/checks.py`:**
```python
"""Core validation functions for checkpl."""
```

**Create `tests/__init__.py`:**
```python
# Empty file - marks tests as a Python package
```

**Create `tests/test_checks.py`:**
```python
"""Tests for checkpl validation functions."""
```

---

## 1.6 Update `src/checkpl/__init__.py`

Replace the contents with:

```python
"""checkpl - Simple inline data validation for Polars."""

__version__ = "0.0.1"
```

(We'll add exports later once we implement the functions)

---

## 1.7 Verify Setup Works

**Check that Python runs:**
```bash
uv run python -c "import checkpl; print(checkpl.__version__)"
```

Expected output:
```
0.0.1
```

**Check that pytest runs (no tests yet, that's ok):**
```bash
uv run pytest -v
```

Expected output:
```
collected 0 items
```

**Check that ruff runs:**
```bash
uv run ruff check src/ tests/
```

Expected output: no errors (or empty output)

---

## Checklist

- [ ] Ran `uv add polars`
- [ ] Ran `uv add --dev pytest ruff`
- [ ] Created `tests/` directory
- [ ] Updated `pyproject.toml`
- [ ] Created empty `src/checkpl/errors.py`
- [ ] Created empty `src/checkpl/checks.py`
- [ ] Created empty `tests/__init__.py`
- [ ] Created empty `tests/test_checks.py`
- [ ] Updated `src/checkpl/__init__.py` with version
- [ ] Verified `uv run python -c "import checkpl"` works
- [ ] Verified `uv run pytest` runs without errors

---

## Next Step

Once all checks pass, proceed to `2__errors.md` to implement `CheckError`.
