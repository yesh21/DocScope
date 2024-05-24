from langchain_community.llms import LlamaCpp
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_core.runnables import RunnableConfig
from prompt import Mistral_7b_sql_prompt
from prompt import Mistral_7b_python_plot_prompt
from prompt import Mistral_7b_rag_prompt
import streamlit as st
from database import ConnectDB
from RAG import get_compressed_docs
from RAG import doc_retrieval

from plotter import st_plotter
import io
import pandas as pd
import re


@st.cache_resource
def llm_model(model_path, n_gpu_layers, temperature, n_ctx):
    # st_callback = StreamlitCallbackHandler(st.container())

    llm = LlamaCpp(
        model_path=model_path,
        n_gpu_layers=n_gpu_layers,
        n_batch=512,
        n_ctx=n_ctx,
        f16_kv=True,
        # callback_manager=st_callback,
        verbose=True,
        temperature=temperature,
    )
    return llm


def get_prompt(question, file_extension):

    if isinstance(
        st.session_state.current_file,
        st.runtime.uploaded_file_manager.UploadedFile,
    ):

        if file_extension in ["db", "sql", "csv", "xlsx"]:

            plot_command = question[:5] if len(question) >= 5 else question
            st.session_state.plot_df.dropna()

            if not st.session_state.plot_df.empty and plot_command.lower() == "plot$":

                buffer = io.StringIO()
                st.session_state.plot_df.info(buf=buffer)
                s = buffer.getvalue()
                lines = s.splitlines()
                buffer.close()
                df_info = "\n".join(lines[:-2])
                return Mistral_7b_python_plot_prompt(question, df_info)

            sql_schema = st.session_state.selected_schemas
            return Mistral_7b_sql_prompt(question, sql_schema)

        elif file_extension in ["pdf", "docx", "txt", "html"]:

            vectordb = doc_retrieval(st.session_state.current_file, file_extension)
            retrieved_chunk = get_compressed_docs(vectordb, question)
            return Mistral_7b_rag_prompt(question, retrieved_chunk)

        else:
            return question

    if st.session_state.user_custom_prompt != "":
        # Define the pattern to match "{question}"
        pattern = r"\{question\}"

        # Replace "{question}" with actual question
        question = re.sub(pattern, question, st.session_state.user_custom_prompt)

    return question


def get_manual_query(file_name):

    manual_query = st.session_state.manual_query_value

    sol1 = ConnectDB(
        "tempfiles/" + file_name + ".db",
        manual_query,
    )
    if sol1:

        columns = [x[0] for x in sol1[1]]
        st.session_state.plot_df = pd.DataFrame(sol1[0], columns=columns)
    else:
        st.session_state.plot_df = pd.DataFrame()

    st.session_state.chat_history.append(
        {
            "role": "manual",
            "content": manual_query,
        },
    )

    print("manual query")


class RunLLM:
    def __init__(self):
        pass

    def load_model(self):
        chatbox = st.container()
        for i in st.session_state.chat_history:
            if i["role"] == "user":
                chatbox.chat_message("user").write(i["content"])

            elif i["role"] == "manual":
                chatbox.chat_message("manual").write(i["content"])

            else:

                with chatbox.expander("See Generated Response"):
                    st.chat_message(i["role"]).write(i["content"])

        if question := st.chat_input("Say something"):

            chatbox.chat_message("user").write(question)
            st.session_state.chat_history.append(
                {
                    "role": "user",
                    "content": question,
                }
            )
            model = llm_model(**st.session_state.llm_settings)
            with st.spinner("Generating reponse..."):

                answer_container = chatbox.chat_message("assistant")
                st_callback = StreamlitCallbackHandler(answer_container)
                cfg = RunnableConfig()
                cfg["callbacks"] = [st_callback]

                file_extension = None
                file_name = None

                if isinstance(
                    st.session_state.current_file,
                    st.runtime.uploaded_file_manager.UploadedFile,
                ):
                    file_extension = st.session_state.current_file.name.split(".")[
                        -1
                    ].lower()
                    file_name = st.session_state.current_file.name.split(".")[0]

                custom_prompt = get_prompt(question, file_extension)

                output = model.invoke(
                    custom_prompt, max_tokens=2048, echo=True, config=cfg
                )
                # chatbox.chat_message("assistant").write(output)

                st_callback._current_thought._container.update(
                    label="",
                    state="complete",
                    expanded=True,
                )

                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": output,
                    },
                )
                plot_command = question[:5] if len(question) >= 5 else question

                if file_extension in ["db", "sql", "csv", "xlsx"]:
                    file_name = re.sub(r"[^a-zA-Z0-9_]", "", file_name)

                    if not plot_command.lower() == "plot$":
                        worked = False

                        if st.session_state.auto_execute_sql:  # autoexecute

                            sol = ConnectDB("tempfiles/" + file_name + ".db", output)
                            if sol:
                                worked = True
                                columns = [x[0] for x in sol[1]]
                                st.session_state.plot_df = pd.DataFrame(
                                    sol[0], columns=columns
                                )
                                st.dataframe(st.session_state.plot_df)

                        if (
                            not st.session_state.auto_execute_sql or not worked
                        ):  # autoexecute off or sql didn't work properly

                            value = ""
                            if not st.session_state.auto_execute_sql:
                                value = output
                                st.markdown("```Auto executer turned off```")

                            with st.form("chat_input_form"):
                                # Create two columns; adjust the ratio to your liking
                                col1, col2 = st.columns([3, 1])

                                col1.text_input(
                                    label="Wanna try Querying manually or rephrase?",
                                    placeholder="Wanna try Querying manually or rephrase?",
                                    value=value,
                                    key="manual_query_value",
                                    label_visibility="collapsed",
                                )

                                col2.form_submit_button(
                                    "Execute",
                                    on_click=get_manual_query,
                                    args=[file_name],
                                )

                    else:
                        st_plotter(output)
                        pass
