from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.documents import Document
import os
import streamlit as st
from .chroma_utils import vectorstore
from dotenv import load_dotenv
load_dotenv()

os.environ["GROQ_API_KEY"]=st.secrets["GROQ_API_KEY"]

contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "Given a chat history and the latest user question which might reference context,"
        " reformulate a standalone question understandable without history."
        " In case the chat history is empty or the question is standalone then return the question as it is"
        " Donot answer the question and return the reformed question."
    )),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant. Use the following context to answer the question."),
    ("system", "Context: {context}"),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

class CustomRetriever:
    def __init__(self, collection, k: int = 2):
        self.collection = collection
        self.k = k
    def __call__(self, question: str):
        results = self.collection.query(query_texts=[question], n_results=self.k)
        return [Document(page_content=text, metadata=meta or {})
                for text, meta in zip(results['documents'][0], results.get('metadatas', [[]])[0])]

def contextualise_q(query, chat=[], model: str = "llama3-70b-8192"):
    llm = ChatGroq(model=model)
    reformulated = contextualize_q_prompt.invoke({"input": query, "chat_history": chat})
    answer = llm.invoke(reformulated)
    return answer.content

def get_rag_chain(query, chat, model: str = "llama3-70b-8192"):
    llm = ChatGroq(model=model)
    retriever = CustomRetriever(vectorstore)
    content=retriever.__call__(query)
    reformulated = qa_prompt.invoke({"context":content, "input":query, "chat_history": chat})
    answer = llm.invoke(reformulated)
    return answer.content