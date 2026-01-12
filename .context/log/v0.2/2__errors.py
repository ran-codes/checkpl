"""Scratch script to test CheckError implementation."""
print('hi')
from assert_polars import hello
from assert_polarserrors import CheckError

# Test 1: hello() still works
print("=== Test 1: hello() ===")
print(hello())

# Test 2: Create a CheckError
print("\n=== Test 2: Create CheckError ===")
e = CheckError("test message", check_name="is_uniq")
print(f"Message: {e}")
print(f"Check name: {e.check_name}")

# Test 3: Raise and catch CheckError
print("\n=== Test 3: Raise and catch ===")
try:
    raise CheckError("validation failed", check_name="not_null")
except CheckError as caught:
    print(f"Caught error: {caught}")
    print(f"Check name: {caught.check_name}")

# Test 4: CheckError without check_name (optional param)
print("\n=== Test 4: Without check_name ===")
e2 = CheckError("simple error")
print(f"Message: {e2}")
print(f"Check name: {e2.check_name}")  # Should be None

print("\n=== All tests passed! ===")
