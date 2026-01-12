"""Tests for is_uniq() predicate."""

import polars as pl
import pytest

from checkpl import verify, is_uniq, CheckError


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
