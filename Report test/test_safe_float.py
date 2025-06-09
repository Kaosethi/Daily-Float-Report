from generate_report import safe_float

def test_valid_float_string():
    result = safe_float("1,234.56")
    print(f"safe_float('1,234.56') returned: {result!r}")  # Expect 1234.56

def test_invalid_string():
    result = safe_float("abc")
    print(f"safe_float('abc') returned: {result!r}")  # Expect None

def test_none_input():
    result = safe_float(None)
    print(f"safe_float(None) returned: {result!r}")  # Expect None

if __name__ == "__main__":
    test_valid_float_string()
    test_invalid_string()
    test_none_input()
