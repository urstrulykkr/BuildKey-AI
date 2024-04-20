
from dotenv import load_dotenv
import os
from PyPDF2 import PdfReader
import streamlit as st
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_community.llms import OpenAI
from langchain.callbacks import get_openai_callback
import streamlit.components.v1 as components

import langchain
langchain.verbose = False

# load environment variables
load_dotenv()

# process text from pdf
def process_text(text):
    # split the text into chunks using langchain
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )

    chunks = text_splitter.split_text(text)

    # convert the chunks of text into embeddings to form a knowledge base
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get("OPENAI_API_KEY"))

    knowledge_base = FAISS.from_texts(chunks, embeddings)

    return knowledge_base

def main():
    st.title("🌉 BuildKey AI - Copilot for TeamOps")
    st.subheader("Access Data In ⚡ Seconds")

    pdf = './HiveBuildDoc.pdf'

    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        
        # store the pdf text in a var
        text = ""

        for page in pdf_reader.pages:
            text += page.extract_text()

        # create a knowledge base object
        knowledgeBase = process_text(text)

    query = st.text_input('Enter your query or type "map" to view the interactive map')

    cancel_button = st.button('Clear')

    if cancel_button:
      st.stop()

    if query.lower() == "map":
        # URL of the map to be embedded
        map_url = "https://chart.maryland.gov/InteractiveMap/GetInteractiveMap"
        # Using an iframe to embed the map
        components.iframe(map_url, height=600, scrolling=True)
    elif query:
        docs = knowledgeBase.similarity_search(query)
        llm = OpenAI(openai_api_key=os.environ.get("OPENAI_API_KEY"))
        chain = load_qa_chain(llm, chain_type="stuff")
        
        with get_openai_callback() as cost:
            response = chain.invoke(input={"question": query, "input_documents": docs})
            print(cost)

            st.write(response["output_text"])

if __name__ == "__main__":
    main()
