"""Scratch script to test verify() implementation."""

import polars as pl
from assert_polars import verify

# Test 1: Polars expression - passes
print("=== Test 1: Expression passes ===")
df = pl.DataFrame({"x": [1, 2, 3]})
df.pipe(verify(pl.col("x") > 0))

# Test 2: Polars expression - fails
print("\n=== Test 2: Expression fails ===")
df_bad = pl.DataFrame({"x": [1, -1, 3]})
df_bad.pipe(verify(pl.col("x") > 0))


# Test 3: Works with LazyFrame
print("\n=== Test 3: LazyFrame ===")
lf = pl.LazyFrame({"x": [1, 2, 3]})
result_lazy = lf.pipe(verify(pl.col("x") > 0))
print(f"Type: {type(result_lazy).__name__}")

# Test 4: Complex expression
print("\n=== Test 4: Complex expression ===")
df2 = pl.DataFrame({"status": ["A", "B", "A"]})
result2 = df2.pipe(verify(pl.col("status").is_in(["A", "B"])))
print(f"Passed! Shape: {result2.shape}")

# Test 5: Callable predicate (mock for now)
print("\n=== Test 5: Callable predicate ===")
def mock_predicate(df):
    """Mock predicate that always passes."""
    print("  Mock predicate called!")
    return df

result3 = df.pipe(verify(mock_predicate))
print(f"Passed! Shape: {result3.shape}")

# Test 6: Invalid type
print("\n=== Test 6: Invalid type ===")
try:
    df.pipe(verify("not valid"))
except TypeError as e:
    print(f"Caught TypeError: {e}")

print("\n=== All tests passed! ===")
