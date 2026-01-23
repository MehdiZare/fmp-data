# tests/unit/test_helpers.py
"""Tests for the deprecated decorator in fmp_data/helpers.py"""

import warnings

from fmp_data.helpers import deprecated


class TestDeprecatedDecorator:
    """Tests for the @deprecated decorator"""

    def test_deprecated_without_reason(self):
        """Test deprecated decorator without a reason"""

        @deprecated()
        def old_function():
            return "result"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = old_function()

            assert result == "result"
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "old_function is deprecated." in str(w[0].message)

    def test_deprecated_with_reason(self):
        """Test deprecated decorator with a reason"""

        @deprecated("Use new_function instead.")
        def old_function():
            return "result"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = old_function()

            assert result == "result"
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "old_function is deprecated." in str(w[0].message)
            assert "Use new_function instead." in str(w[0].message)

    def test_deprecated_preserves_function_name(self):
        """Test that deprecated decorator preserves function metadata"""

        @deprecated("Reason")
        def documented_function():
            """This is a docstring."""
            pass

        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "This is a docstring."

    def test_deprecated_with_arguments(self):
        """Test deprecated decorator with function arguments"""

        @deprecated("Old API")
        def add_numbers(a: int, b: int) -> int:
            return a + b

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = add_numbers(2, 3)

            assert result == 5
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)

    def test_deprecated_with_kwargs(self):
        """Test deprecated decorator with keyword arguments"""

        @deprecated()
        def greet(name: str, greeting: str = "Hello") -> str:
            return f"{greeting}, {name}!"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = greet("World", greeting="Hi")

            assert result == "Hi, World!"
            assert len(w) == 1

    def test_deprecated_multiple_calls(self):
        """Test that warning is raised on each call"""

        @deprecated("Old function")
        def old_func():
            return True

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            old_func()
            old_func()
            old_func()

            assert len(w) == 3
            for warning in w:
                assert issubclass(warning.category, DeprecationWarning)

    def test_deprecated_on_method(self):
        """Test deprecated decorator on class method"""

        class MyClass:
            @deprecated("Use new_method instead")
            def old_method(self):
                return "old result"

        obj = MyClass()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = obj.old_method()

            assert result == "old result"
            assert len(w) == 1
            assert "old_method is deprecated." in str(w[0].message)
