import streamlit as st
import chromadb
import os
from dotenv import load_dotenv
from openai import OpenAI

# 1. Configuration & Setup
st.set_page_config(page_title="My RAG Assistant", page_icon="🤖")
load_dotenv()

# Initialize Clients (Cached so they don't reload on every click)
@st.cache_resource
def get_clients():
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_collection(name="knowledge_base")
    return openai_client, collection

openai_client, collection = get_clients()

# Helper Functions (Same as yesterday)
def get_embedding(text):
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def query_database(query_text):
    results = collection.query(
        query_embeddings=[get_embedding(query_text)],
        n_results=1
    )
    if not results['documents'][0]:
        return None, None
    
    # Return both the text AND the source filename
    return results['documents'][0][0], results['metadatas'][0][0]

def generate_answer(query, context):
    prompt = f"""
    You are a helpful assistant. Use the provided context to answer the question.
    Context: {context}
    Question: {query}
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# 2. The App Interface
st.title("🤖 Chat with your PDF")
st.write("Ask a question about the documents you uploaded.")

# Input Box
user_query = st.text_input("Enter your question:", placeholder="e.g., What is the invoice total?")

if user_query:
    with st.spinner("Thinking..."):
        # A. Search
        retrieved_context, metadata = query_database(user_query)
        
        if retrieved_context:
            # B. Generate
            answer = generate_answer(user_query, retrieved_context)
            
            # C. Display Result
            st.success("Answer found!")
            st.markdown(f"### 💡 AI Answer:\n{answer}")
            
            # D. Display Source (Transparency)
            st.info(f"📖 Source: `{metadata['source']}`")
            with st.expander("See raw context"):
                st.write(retrieved_context)
        else:
            st.warning("No relevant information found in the database.")