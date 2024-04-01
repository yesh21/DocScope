from langchain.prompts import PromptTemplate


def Mistral_7b_sql_prompt(query: str, sql_schema: str) -> str:

    text = """
    <s>[INST] Generate a correct SQL query from the following database schema.
    {sql_schema}
    {query}
    [/INST]"""

    prompt = PromptTemplate(
        input_variables=["sql_schema", "query"],
        template=text,
    )

    # format the prompt to add variable values
    prompt_formatted_str = prompt.format(sql_schema=sql_schema, query=query)

    return prompt_formatted_str


def Mistral_7b_python_plot_prompt(query: str, pandas_df_info) -> str:

    text = """
    <s>[INST] you are an expert python programmer.
    You are given a csv pandas dataframe with the dataframe info:
    {pandas_df_info}
    you should read the csv file, and plot the query
    Query: {query}
    [/INST]
    """

    prompt = PromptTemplate(
        input_variables=["pandas_df_info", "query"],
        template=text,
    )

    # format the prompt to add variable values
    prompt_formatted_str = prompt.format(pandas_df_info=pandas_df_info, query=query)

    return prompt_formatted_str


def Mistral_7b_rag_prompt(query: str, retrieved_chunk: str) -> str:

    text = """
    [INST]
    Context information is below.
    ---------------------
    {retrieved_chunk}
    ---------------------
    Given the context information and not prior knowledge, answer the query.
    Query: {query}
    Answer:[/INST]
    """

    prompt = PromptTemplate(
        input_variables=["retrieved_chunk", "query"],
        template=text,
    )

    # format the prompt to add variable values
    prompt_formatted_str = prompt.format(retrieved_chunk=retrieved_chunk, query=query)

    return prompt_formatted_str
