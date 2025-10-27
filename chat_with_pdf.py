import streamlit as st
import os
from openai import OpenAI
from os import environ

from RagFunction import *

#----- init ----#
client = OpenAI(
	api_key=os.environ["API_KEY"],
	base_url="https://api.ai.it.cornell.edu",
)

st.title("📝 Multi Files Q&A with OpenAI")

if "previous_file_list" not in st.session_state:
    st.session_state.previous_file_list = set() 

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Ask something about the article"}]

if "rag_manager" not in st.session_state:
    st.toast("init RAG...")
    st.session_state.rag_manager = RAG()

#----- handle files -----#


uploaded_files_widget = st.file_uploader(
    "Upload one or more files(txt, md, pdf)",
    type=("txt", "md", "pdf"),
    accept_multiple_files=True,
    key="all_uploaded_files"
)

current_files_in_widget = st.session_state.all_uploaded_files
current_file_names = {file.name for file in current_files_in_widget}

previous_file_names = st.session_state.previous_file_list

rag_manager = st.session_state.rag_manager
is_update = rag_manager.handle_files(current_file_names, previous_file_names, current_files_in_widget)

if is_update:
    st.session_state.previous_file_list = current_file_names

#----- handle message -----#
question = st.chat_input(
    "Ask something about the article",
    disabled=not st.session_state.all_uploaded_files,
)

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

#----- handle model -----#
if question and st.session_state.all_uploaded_files:

    st.toast("RAG Retrieving (MMR)...")
    # Append the user's question to the messages
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user").write(question)

    try:
        retrieved_docs = rag_manager.retrieve_chunks(question, search_type="mmr", k=5)
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])
        print(context)
    except Exception as e:
        st.error(f"Retrieving Error: {e}")
        context = "Retrieving Error. No Context."

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="openai.gpt-4o",  # Change this to a valid model name
            messages=[
                {"role": "system", "content": f"Here's the relevant context retrieved from the file:\n\n{context}"},
                *st.session_state.messages
            ],
            stream=True
        )
        response = st.write_stream(stream)

    # Append the assistant's response to the messages
    st.session_state.messages.append({"role": "assistant", "content": response})