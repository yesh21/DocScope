import streamlit as st
import os
from schema import getschemafromdb
from database import CreateDBformSQL
import pandas as pd
from database import Pandasdb
from llm import RunLLM
import re


def set_page_config():
    """Sets the page configuration."""
    st.set_page_config(
        page_title="DocScope",
        layout="wide",
    )


def session_variables():
    # Initialize the chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "selected_schemas" not in st.session_state:
        st.session_state.selected_schemas = ""

    if "ddl_ddl_dict" not in st.session_state:
        st.session_state.ddl_ddl_dict = {"NA_tables": "NA"}

    if "plot_df" not in st.session_state:
        st.session_state.plot_df = pd.DataFrame()

    if "llm_settings" not in st.session_state:
        st.session_state.llm_settings = {
            "model_path": "/Users/yaswanthpulavarthi/Works/llm_models/Mistral-7B-Instruct-SQL-Mistral-7B-Instruct-v0.2-slerp.Q4_K_M.gguf",
            "n_gpu_layers": 40,
            "temperature": 0.0,
            "n_ctx": 2048,
        }
    if "user_custom_prompt" not in st.session_state:
        st.session_state.user_custom_prompt = ""

    if "auto_execute_sql" not in st.session_state:
        st.session_state.auto_execute_sql = True


# Define the Streamlit app
def app():
    set_page_config()

    col1, _, col2 = st.columns([3, 1, 1])
    with col1:

        st.markdown("# :blue[DocScope]: Local LLM Doc Analysis Tool :sunglasses:")

    with col2:

        with st.popover("Custom :blue[template]"):

            st.markdown("Format: use `{question}` to add chat query in ```TEMPLATE```")
            user_template = st.text_area("Add custom template here?")
            template_submit_button = st.button("submit")
            if template_submit_button:

                pattern = r"\{question\}"
                pattern_count = len(re.findall(pattern, user_template))

                st.session_state.user_custom_prompt = user_template

                if pattern_count == 0:
                    st.warning(
                        "pattern ```{question}``` not found, so added at last to template"
                    )
                    st.session_state.user_custom_prompt = user_template + " {question}"

                elif pattern_count == 1:
                    st.success("prompt upadated")
                else:
                    st.warning(
                        "WARNING: multiple ```{question}``` patterns are present"
                    )

    custom_css = """
    <style>
    /* Add your custom CSS styles here */
    [data-testid="column"] {
      align-self: center;
    }
    </style>
    """

    # Inject custom CSS styles
    st.markdown(custom_css, unsafe_allow_html=True)

    session_variables()

    def file_on_change():
        if st.session_state.current_file:
            st.sidebar.markdown(
                f"""`Current file`: `{st.session_state.current_file.name}`"""
            )
            st.balloons()
        else:
            st.sidebar.markdown("`Current file`: `None`")

    with st.sidebar.form(key="my_form"):
        uploaded_file = st.file_uploader(
            "Upload File",
            type=["csv", "xlsx", "pdf", "db", "sql", "txt", "docx", "html"],
            key="current_file",
        )
        file_submit_button = st.form_submit_button(
            label="Upload", on_click=file_on_change, type="primary"
        )

    # SQL schema and LLM settings
    st.sidebar.divider()

    auto_sql_toggle = st.sidebar.toggle("Auto SQL execution", value=True)
    if auto_sql_toggle:

        st.session_state.auto_execute_sql = True
    else:
        st.session_state.auto_execute_sql = False

    selected_table = st.sidebar.multiselect(
        "Select a table:",
        options=list(st.session_state.ddl_ddl_dict.keys()),
        default=["NA_tables"],
    )

    # Ensure at least one value is selected
    if len(selected_table) == 0:
        selected_table = ["NA_tables"]
        st.session_state.selected_schemas = ""

    else:
        st.session_state.selected_schemas = "\n".join(
            [
                st.session_state.ddl_ddl_dict[x]
                for x in selected_table
                if x != "NA_tables"
            ]
        )

    if st.session_state.selected_schemas != "":

        st.sidebar.markdown(f"### DDL Schema for {selected_table} table/s")
        st.sidebar.code(st.session_state.selected_schemas)
    else:

        st.sidebar.markdown("### Select table/s to get DDL schema")
        st.sidebar.code("None")

    with st.sidebar.expander(":rainbow[**LLM Setting**]"):
        # Advanced LLM Settings (for the curious minds!)
        with st.form("llm_setting_form", border=False):

            model_path = st.text_input("enter path of gguf file:")
            n_gpu_layers = st.slider(
                "number of GPU layers",
                value=40,
                min_value=1,
                max_value=50,
                step=1,
            )
            temperature = st.slider(
                "Temperature of model",
                value=0.0,
                min_value=0.0,
                max_value=1.0,
                step=0.1,
            )
            n_ctx = st.slider(
                "Context window size",
                value=1024,
                min_value=128,
                max_value=2048,
                step=32,
            )

            llm_sett_submit = st.form_submit_button("Submit")

            if llm_sett_submit:
                if os.path.exists(model_path):
                    st.session_state.llm_settings.update(
                        model_path=model_path,
                        n_gpu_layers=n_gpu_layers,
                        temperature=temperature,
                        n_ctx=n_ctx,
                    )

                    st.success("Updated LLM settings")
                else:
                    st.warning("Invalid: Model PATH dont exist...")

    if file_submit_button:
        # Process the uploaded file here
        if uploaded_file is not None:

            file_extension = uploaded_file.name.split(".")[-1].lower()
            file_name = re.sub(r"[^a-zA-Z0-9_]", "", uploaded_file.name.split(".")[0])
            if file_extension == "db" or file_extension == "sql":
                with open(os.path.join("tempfiles", uploaded_file.name), "wb") as f:
                    f.write(uploaded_file.getbuffer())

            if (
                file_extension == "pdf"
                or file_extension == "txt"
                or file_extension == "docx"
                or file_extension == "html"
            ):
                st.write("Text BASED file uploaded")

            elif file_extension == "db":
                results = getschemafromdb("tempfiles/" + file_name + ".db")
                st.session_state.ddl_ddl_dict = results

            elif file_extension == "csv":

                df = pd.read_csv(uploaded_file)
                df.columns = df.columns.str.replace("[^a-zA-Z0-9]", "", regex=True)

                Pandasdb(file_name, df)

                results = getschemafromdb("tempfiles/" + file_name + ".db")
                st.session_state.ddl_ddl_dict = results

            elif file_extension == "xlsx":
                # Load the Excel file
                xls = pd.ExcelFile(uploaded_file)

                # Get the sheet names
                sheet_names = xls.sheet_names
                for sheet_name in sheet_names:

                    df = pd.read_excel(xls, sheet_name)
                    df.columns = df.columns.str.replace("[^a-zA-Z0-9]", "", regex=True)
                    Pandasdb(file_name, df)

                results = getschemafromdb("tempfiles/" + file_name + ".db")
                st.session_state.ddl_ddl_dict = results

            elif file_extension == "sql":

                CreateDBformSQL("tempfiles/" + file_name)
                results = getschemafromdb("tempfiles/" + file_name + ".db")
                st.session_state.ddl_ddl_dict = results

            else:

                st.write("Not valid format")

    check = RunLLM()
    check.load_model()

    if st.session_state.chat_history:
        if st.session_state.chat_history[-1]["role"] == "manual":
            st.dataframe(st.session_state.plot_df)


# Run the app
if __name__ == "__main__":
    app()
