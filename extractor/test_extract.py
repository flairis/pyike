from extract import extract_func, FunctionDefinition


def test_extract_function():
    def f(x: int, y: int) -> int:
        """This is the summary.

        This is the description.

        Args:
            x: The first argument.
            y: The second argument.

        Returns:
            The sum of x and y.
        """
        return x + y

    definition = extract_func(f)

    assert definition == FunctionDefinition(
        name="test_extract.test_extract_function.<locals>.f",
        signature="test_extract.test_extract_function.<locals>.f(x: int, y: int) -> int",
        summary="This is the summary.",
        desc="This is the description.",
        args=[
            {"name": "x", "type": None, "desc": "The first argument."},
            {"name": "y", "type": None, "desc": "The second argument."},
        ],
        returns="The sum of x and y.",
        examples=[],
    )


def test_extract_class():
    def f(x: int, y: int) -> int:
        """This is the summary.

        This is the description.

        Args:
            x: The first argument.
            y: The second argument.

        Returns:
            The sum of x and y.
        """
        return x + y

    definition = extract_func(f)

    assert definition == FunctionDefinition(
        name="test_extract.test_extract_function.<locals>.f",
        signature="test_extract.test_extract_function.<locals>.f(x: int, y: int) -> int",
        summary="This is the summary.",
        desc="This is the description.",
        args=[
            {"name": "x", "type": None, "desc": "The first argument."},
            {"name": "y", "type": None, "desc": "The second argument."},
        ],
        returns="The sum of x and y.",
        examples=[],
    )
