"""Verify function - main entry point for all validation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Union

import polars as pl

from checkpl.errors import CheckError

if TYPE_CHECKING:
    pass

# Type alias for both DataFrame types
FrameType = pl.DataFrame | pl.LazyFrame

# Type for what verify() accepts: expression or callable predicate
CheckType = Union[pl.Expr, Callable[[FrameType], FrameType]]


def _to_scalar(result: pl.DataFrame | pl.LazyFrame):
    """Collect LazyFrame if needed and extract single scalar value."""
    if isinstance(result, pl.LazyFrame):
        result = result.collect()
    return result.item()


def verify(check: CheckType) -> Callable[[FrameType], FrameType]:
    """
    Verify a DataFrame using a Polars expression or predicate.

    This is the main entry point for all checkpl validation.

    Usage:
        # With Polars expressions
        df.pipe(verify(pl.col('price') > 0))
        df.pipe(verify(pl.col('status').is_in(['A', 'B'])))

        # With predicates
        df.pipe(verify(is_uniq('id', 'date')))
        df.pipe(verify(not_null('name')))

    Args:
        check: Either a Polars expression (pl.Expr) or a predicate callable

    Returns:
        A function that takes a DataFrame and returns it unchanged if valid

    Raises:
        CheckError: If validation fails
    """
    def _verify(df: FrameType) -> FrameType:
        # Case 1: Polars expression
        if isinstance(check, pl.Expr):
            fail_count = _to_scalar(df.select((~check).sum()))
            if fail_count > 0:
                raise CheckError(
                    f"verify failed: {fail_count} row(s) did not satisfy condition",
                    check_name="verify",
                )
            return df

        # Case 2: Callable predicate (is_uniq, not_null, etc.)
        if callable(check):
            return check(df)

        # Case 3: Unknown type
        raise TypeError(
            f"verify() expects pl.Expr or callable, got {type(check).__name__}"
        )

    return _verify
