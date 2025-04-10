"""
Compatibility module for nose.tools imports.
For Python 3.12 where nose is not fully compatible.
"""

try:
    from .nose_compat import assert_equal, assert_raises, assert_almost_equal, assert_not_equal
except ImportError:
    # Fallback for Python 3.12 (imp module removed)
    def assert_equal(a, b, msg=None):
        """Assert that two objects are equal."""
        assert a == b, msg or f"{a!r} != {b!r}"
        
    def assert_not_equal(a, b, msg=None):
        """Assert that two objects are not equal."""
        assert a != b, msg or f"{a!r} == {b!r}"
        
    def assert_raises(exception, callable_obj=None, *args, **kwargs):
        """Assert that calling the callable raises the expected exception."""
        if callable_obj is None:
            return _AssertRaisesContext(exception)
        try:
            callable_obj(*args, **kwargs)
        except exception:
            return
        raise AssertionError(f"{callable_obj} did not raise {exception}")
        
    def assert_almost_equal(a, b, places=7, msg=None, delta=None):
        """Assert that two numbers are almost equal."""
        if delta is not None:
            assert abs(a - b) <= delta, msg or f"{a!r} != {b!r} within {delta} delta"
        else:
            assert round(abs(a - b), places) == 0, msg or f"{a!r} != {b!r} within {places} places"

class _AssertRaisesContext:
    """Context manager for assert_raises."""
    def __init__(self, expected):
        self.expected = expected
        self.exception = None
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is None:
            raise AssertionError(f"Did not raise {self.expected}")
        if not issubclass(exc_type, self.expected):
            return False
        self.exception = exc_value
        return True