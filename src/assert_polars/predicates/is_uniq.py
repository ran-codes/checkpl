"""Uniqueness check predicate."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import polars as pl

from assert_polars.errors import CheckError

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
