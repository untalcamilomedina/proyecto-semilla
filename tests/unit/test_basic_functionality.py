"""
Basic functionality tests that don't require complex dependencies
"""

def test_basic_math():
    """Test basic mathematical operations"""
    assert 2 + 2 == 4
    assert 5 * 3 == 15
    assert 10 - 3 == 7
    assert 20 / 4 == 5

def test_string_operations():
    """Test basic string operations"""
    test_string = "Proyecto Semilla"

    assert len(test_string) == 16
    assert test_string.upper() == "PROYECTO SEMILLA"
    assert test_string.lower() == "proyecto semilla"
    assert "Semilla" in test_string

def test_list_operations():
    """Test basic list operations"""
    test_list = [1, 2, 3, 4, 5]

    assert len(test_list) == 5
    assert sum(test_list) == 15
    assert max(test_list) == 5
    assert min(test_list) == 1

    # Test list comprehension
    squares = [x**2 for x in test_list]
    assert squares == [1, 4, 9, 16, 25]

def test_dictionary_operations():
    """Test basic dictionary operations"""
    test_dict = {
        "name": "Proyecto Semilla",
        "version": "0.1.0",
        "status": "active"
    }

    assert test_dict["name"] == "Proyecto Semilla"
    assert test_dict["version"] == "0.1.0"
    assert test_dict["status"] == "active"
    assert len(test_dict) == 3

def test_boolean_logic():
    """Test boolean logic operations"""
    assert True and True is True
    assert True or False is True
    assert not False is True
    assert (5 > 3) and (10 < 20) is True

def test_none_handling():
    """Test None value handling"""
    value = None

    assert value is None
    assert value is not 0
    assert value is not ""
    assert value is not False

def test_type_checking():
    """Test basic type checking"""
    assert isinstance("string", str)
    assert isinstance(42, int)
    assert isinstance(3.14, float)
    assert isinstance(True, bool)
    assert isinstance([1, 2, 3], list)
    assert isinstance({"key": "value"}, dict)

def test_exception_handling():
    """Test basic exception handling"""
    try:
        result = 10 / 0
        assert False, "Should have raised ZeroDivisionError"
    except ZeroDivisionError:
        assert True  # Expected exception

    try:
        result = int("not_a_number")
        assert False, "Should have raised ValueError"
    except ValueError:
        assert True  # Expected exception

def test_file_operations():
    """Test basic file operations"""
    import os
    import tempfile

    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("test content")
        temp_file = f.name

    try:
        # Read the file
        with open(temp_file, 'r') as f:
            content = f.read()
            assert content == "test content"
    finally:
        # Clean up
        os.unlink(temp_file)

def test_set_operations():
    """Test basic set operations"""
    set1 = {1, 2, 3, 4, 5}
    set2 = {4, 5, 6, 7, 8}

    union = set1 | set2
    intersection = set1 & set2
    difference = set1 - set2

    assert len(union) == 8
    assert len(intersection) == 2
    assert len(difference) == 3
    assert 4 in intersection
    assert 1 not in intersection

def test_tuple_operations():
    """Test basic tuple operations"""
    test_tuple = (1, 2, 3, "four", 5.0)

    assert len(test_tuple) == 5
    assert test_tuple[0] == 1
    assert test_tuple[-1] == 5.0
    assert "four" in test_tuple

    # Test tuple unpacking
    a, b, c, d, e = test_tuple
    assert a == 1
    assert d == "four"

def test_range_operations():
    """Test range operations"""
    r = range(5)

    assert list(r) == [0, 1, 2, 3, 4]
    assert len(r) == 5
    assert 3 in r
    assert 10 not in r

def test_assertion_methods():
    """Test various assertion methods"""
    # Test equality
    assert 1 == 1
    assert "test" == "test"

    # Test inequality
    assert 1 != 2
    assert "test" != "other"

    # Test comparisons
    assert 5 > 3
    assert 3 < 5
    assert 5 >= 5
    assert 3 <= 5

def test_function_operations():
    """Test function operations"""
    def add_numbers(a, b):
        return a + b

    def multiply_by_two(x):
        return x * 2

    # Test function calls
    assert add_numbers(3, 5) == 8
    assert multiply_by_two(7) == 14

    # Test function as parameter
    def apply_function(func, value):
        return func(value)

    assert apply_function(multiply_by_two, 10) == 20
    assert apply_function(lambda x: x ** 2, 4) == 16