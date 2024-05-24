import os
import tempfile
import streamlit as st
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import BSHTMLLoader


def doc_retrieval(uploaded_file, extension_type):
    persist_directory = f"tempfiles/vectordb/{uploaded_file.name}"
    if not os.path.exists(persist_directory):
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        with st.spinner("Retrieving Document..."):

            if extension_type == "pdf":
                loader = PyMuPDFLoader(file_path=tmp_file_path)
                data = loader.load()

            if extension_type == "txt":
                data = TextLoader(file_path=tmp_file_path).load()

            if extension_type == "docx":
                data = Docx2txtLoader(file_path=tmp_file_path).load()

            if extension_type == "html":
                data = BSHTMLLoader(file_path=tmp_file_path).load()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=256, chunk_overlap=32
            )

            splits = text_splitter.split_documents(data)

            embeddings = HuggingFaceEmbeddings()

            vectordb = FAISS.from_documents(splits, embeddings)

            vectordb.save_local(f"tempfiles/vectordb/{uploaded_file.name}")

    else:
        embeddings = HuggingFaceEmbeddings()
        vectordb = FAISS.load_local(
            f"tempfiles/vectordb/{uploaded_file.name}",
            embeddings,
            allow_dangerous_deserialization=True,
        )

    return vectordb


def get_compressed_docs(vectordb, query):

    compressed_docs = vectordb.similarity_search(query, k=5)

    return compressed_docs
