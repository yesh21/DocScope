from utils import get_substring_between_delimiters


def test_python_code_extraction():
    output = """
    here is the code in python to print "hello world". 
    ```python
    print("Hello world")
    ```
    """

    assert (
        get_substring_between_delimiters(output, "```python", "```")
        == """
    print("Hello world")
    """
    )
