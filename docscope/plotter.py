from contextlib import contextmanager, redirect_stdout
from io import StringIO
import streamlit as st
from utils import get_substring_between_delimiters
import re


@contextmanager
def st_capture(output_func):
    with StringIO() as stdout, redirect_stdout(stdout):
        old_write = stdout.write

        def new_write(string):
            ret = old_write(string)
            output_func(stdout.getvalue())
            return ret

        stdout.write = new_write
        yield


def executer(py_code: str):
    output = st.empty()
    with st_capture(output.code):
        try:
            exec(py_code)
        except Exception as e:
            print("An exception occurred:", e)


def st_plotter(output: str):

    py_code = get_substring_between_delimiters(output, "```python", "```")
    # Define the pattern to match "pd.read_csv(<something>)"
    read_csv_pattern = r"pd\.read_csv\([^)]*\)"

    # Replace "pd.read_csv(<something>)" with pandas df
    modified_py_code = re.sub(read_csv_pattern, "st.session_state.plot_df", py_code)

    # Define the pattern to match "<something>.show()"
    pattern = r"(\w+)\.show\(\)"

    # Replace "<something>.show()" with "st.pyplot(<something>)"
    modified_py_code = re.sub(
        pattern,
        r"""col1, col2, col3 = st.columns(3)
with col1:
    st.pyplot(\1)""",
        modified_py_code,
    )

    executer(modified_py_code)
