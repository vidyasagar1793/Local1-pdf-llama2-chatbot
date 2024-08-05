import os
import time
import streamlit as st
from llm_interface import stream_response, search_pdf
from llama_index.core import VectorStoreIndex, ServiceContext, SimpleDirectoryReader


def save_uploaded_file(uploaded_file):
    """
    Saves an uploaded file to a specified directory.

    Args:
    - uploaded_file: Uploaded file object to be saved.

    Returns:
    - An acknowledgment message upon successful saving of the file.

    Raises:
    - Any exceptions raised during the file saving process.

    Notes:
    - This function assumes the existence of a 'data' directory in the current working directory.
    - If the directory does not exist, an appropriate exception will be raised.
    """
    with open(os.path.join("data", uploaded_file.name), "wb") as file:
        file.write(uploaded_file.getbuffer())
    return st.sidebar.success(f"Saved PDF file: {uploaded_file.name} to directory")

def main():
    """
    Set app configurations and handle PDF upload, chat history, and user assistant interaction.
    """
    # Set app configurations
    st.set_page_config(page_title="BotPDF", page_icon="🤖")
    st.title("🤖 BotPDF")
    st.caption(body=
        """
        A streamlit chatbot powered by 🦙 Llama2 
        <acronym title="Large Language Model">LLM</acronym> with simple 
        <acronym title="Retrieval Augmented Generation">RAG</acronym>.
        """,
        unsafe_allow_html=True)
    st.divider()

    if os.path.exists('data') is False:
        os.mkdir('data')

    # Add sidebar with PDF uploader
    st.sidebar.title("📤 Upload PDF")
    st.sidebar.caption("Have the assistant take a look at your PDF file")
    uploaded_pdf = st.sidebar.file_uploader(label="Upload a PDF file", type=["pdf"])

    # Save the file once uploaded
    if uploaded_pdf is not None:
        save_uploaded_file(uploaded_pdf)

    # Initialize chat history
    try:
        if "messages" not in st.session_state:
            st.session_state["messages"] = []
    except KeyError:
        st.session_state = {}
        st.session_state["messages"] = []

    # Display messages from chat history
    for msg in st.session_state.get("messages", []):
        if msg["role"] == "assistant":
            st.info(msg["content"])
            st.caption(f"Elapsed time: {msg['elapsed_time']}s")
        else:
            st.write(f"You: {msg['content']}")

    # Accept user input
    prompt = st.text_input("You:", key="user_input")
    if prompt:
        # Add user message to chat history
        st.session_state.setdefault("messages", []).append({"role": "user", "content": prompt})

        # Display assistant response in chat message container
        with st.spinner("Generating response..."):
            start_time = time.time()
            if len(os.listdir('data/')) == 0:
                # If no PDFs are uploaded, generate response without querying PDF
                response = stream_response(prompt)
            else:
                # If PDFs are uploaded, query the PDFs
                response = search_pdf(prompt)
            end_time = time.time()
            elapsed_time = round(end_time - start_time, 2)

        # Display assistant's response
        st.info("Assistant:")
        st.write(response)
        st.caption(f"Elapsed time: {elapsed_time}s")

        # Add assistant response to chat history
        st.session_state.setdefault("messages", []).append({"role": "assistant", "content": response, "elapsed_time": elapsed_time})

if __name__ == "__main__":
    main()
