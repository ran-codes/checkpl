"""Tests for verify() function - Polars expressions only."""

import polars as pl
import pytest

from assert_polars import verify, CheckError


class TestVerifyExpressions:
    """Tests for verify() with Polars boolean expressions."""

    def test_passes_when_all_rows_true(self):
        """Expression that all rows satisfy."""
        df = pl.DataFrame({"x": [1, 2, 3]})
        result = df.pipe(verify(pl.col("x") > 0))
        assert result.equals(df)

    def test_fails_when_some_rows_false(self):
        """Expression that some rows don't satisfy."""
        df = pl.DataFrame({"x": [1, -1, 3]})
        with pytest.raises(CheckError, match="1 row"):
            df.pipe(verify(pl.col("x") > 0))

    def test_fails_reports_correct_count(self):
        """Error message shows correct failure count."""
        df = pl.DataFrame({"x": [-1, -2, 3]})
        with pytest.raises(CheckError, match="2 row"):
            df.pipe(verify(pl.col("x") > 0))

    def test_check_name_is_verify(self):
        """CheckError has check_name='verify'."""
        df = pl.DataFrame({"x": [-1]})
        with pytest.raises(CheckError) as exc_info:
            df.pipe(verify(pl.col("x") > 0))
        assert exc_info.value.check_name == "verify"


class TestVerifyPolarsExpressionTypes:
    """Tests for different Polars expression types."""

    def test_comparison_greater_than(self):
        """Works with > comparison."""
        df = pl.DataFrame({"x": [1, 2, 3]})
        result = df.pipe(verify(pl.col("x") > 0))
        assert result.equals(df)

    def test_comparison_less_than(self):
        """Works with < comparison."""
        df = pl.DataFrame({"x": [1, 2, 3]})
        result = df.pipe(verify(pl.col("x") < 10))
        assert result.equals(df)

    def test_comparison_equals(self):
        """Works with == comparison."""
        df = pl.DataFrame({"x": ["a", "a", "a"]})
        result = df.pipe(verify(pl.col("x") == "a"))
        assert result.equals(df)

    def test_is_in_expression(self):
        """Works with is_in() expression."""
        df = pl.DataFrame({"status": ["A", "B", "A"]})
        result = df.pipe(verify(pl.col("status").is_in(["A", "B"])))
        assert result.equals(df)

    def test_is_between_expression(self):
        """Works with is_between() expression."""
        df = pl.DataFrame({"x": [1, 5, 10]})
        result = df.pipe(verify(pl.col("x").is_between(0, 11)))
        assert result.equals(df)

    def test_is_not_null_expression(self):
        """Works with is_not_null() expression."""
        df = pl.DataFrame({"x": [1, 2, 3]})
        result = df.pipe(verify(pl.col("x").is_not_null()))
        assert result.equals(df)

    def test_str_len_expression(self):
        """Works with str.len_chars() expression."""
        df = pl.DataFrame({"name": ["alice", "bob", "carol"]})
        result = df.pipe(verify(pl.col("name").str.len_chars() > 0))
        assert result.equals(df)


class TestVerifyDataFrameTypes:
    """Tests for DataFrame and LazyFrame support."""

    def test_works_with_dataframe(self):
        """Returns DataFrame when given DataFrame."""
        df = pl.DataFrame({"x": [1, 2, 3]})
        result = df.pipe(verify(pl.col("x") > 0))
        assert isinstance(result, pl.DataFrame)

    def test_works_with_lazyframe(self):
        """Returns LazyFrame when given LazyFrame."""
        lf = pl.LazyFrame({"x": [1, 2, 3]})
        result = lf.pipe(verify(pl.col("x") > 0))
        assert isinstance(result, pl.LazyFrame)

    def test_returns_same_type_as_input(self):
        """Output type matches input type."""
        df = pl.DataFrame({"x": [1, 2, 3]})
        lf = pl.LazyFrame({"x": [1, 2, 3]})

        assert type(df.pipe(verify(pl.col("x") > 0))) == type(df)
        assert type(lf.pipe(verify(pl.col("x") > 0))) == type(lf)


class TestVerifyEdgeCases:
    """Edge case tests."""

    def test_empty_dataframe_passes(self):
        """Empty DataFrame passes (no rows to fail)."""
        df = pl.DataFrame({"x": []}).cast({"x": pl.Int64})
        result = df.pipe(verify(pl.col("x") > 0))
        assert result.equals(df)

    def test_single_row_passes(self):
        """Single row DataFrame works."""
        df = pl.DataFrame({"x": [1]})
        result = df.pipe(verify(pl.col("x") > 0))
        assert result.equals(df)

    def test_single_row_fails(self):
        """Single row DataFrame can fail."""
        df = pl.DataFrame({"x": [-1]})
        with pytest.raises(CheckError, match="1 row"):
            df.pipe(verify(pl.col("x") > 0))

    def test_all_rows_fail(self):
        """All rows failing works correctly."""
        df = pl.DataFrame({"x": [-1, -2, -3]})
        with pytest.raises(CheckError, match="3 row"):
            df.pipe(verify(pl.col("x") > 0))

    def test_nulls_in_expression_column(self):
        """Nulls in expression column behavior.

        Note: In Polars, null > 0 evaluates to null (not True or False).
        When we negate with ~, null stays null. When we sum, null is skipped.
        So nulls effectively "pass" the check - they're not counted as failures.
        """
        df = pl.DataFrame({"x": [1, None, 3]})
        result = df.pipe(verify(pl.col("x") > 0))
        assert result.equals(df)

    def test_multiple_columns_in_expression(self):
        """Expression can reference multiple columns."""
        df = pl.DataFrame({"a": [1, 2, 3], "b": [0, 1, 2]})
        result = df.pipe(verify(pl.col("a") > pl.col("b")))
        assert result.equals(df)

    def test_chaining_multiple_verifies(self):
        """Multiple verify() calls can be chained."""
        df = pl.DataFrame({"x": [1, 2, 3], "y": ["a", "b", "c"]})
        result = (
            df
            .pipe(verify(pl.col("x") > 0))
            .pipe(verify(pl.col("y").is_in(["a", "b", "c"])))
        )
        assert result.equals(df)
