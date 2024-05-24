from streamlit.testing.v1 import AppTest


def test_title_markdown_name():
    """A user increments the number input, then clicks Add"""
    at = AppTest.from_file("app.py")
    # Run the app.
    at.run()
    # print(at.markdown[0].value)
    # print(at.sidebar.toggle[0].value)
    assert (
        at.markdown[0].value
        == "# :blue[DocScope]: Local LLM Doc Analysis Tool :sunglasses:"
    )
