import polars as pl
from assert_polars import verify, is_uniq

# --- Should pass ---
df = pl.DataFrame({"id": [1, 2, 3], "year": [2020, 2020, 2021]})
df.pipe(verify(is_uniq("id")))  # unique ids
df.pipe(verify(is_uniq("id", "year")))  # unique composite key

# --- Should fail ---
df2 = pl.DataFrame({"id": [1, 1, 2]})
df2.pipe(verify(is_uniq("id")))  # CheckError: 2 duplicate(s) in ['id']


# --- Should raise ValueError ---
is_uniq()  # ValueError: is_uniq() requires at least one column
