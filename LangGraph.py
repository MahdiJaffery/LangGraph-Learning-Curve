import os
from dotenv import load_dotenv, find_dotenv

try:
    envPath = find_dotenv()

    if not envPath:
        raise ModuleNotFoundError(".env FILE NOT FOUND")
    if not load_dotenv(envPath):
        raise EnvironmentError("FAILED TO LOAD .env")
    
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    openai_model = os.environ.get("OPENAI_MODEL")

    if not openai_api_key:
        raise ValueError("API NOT FOUND")
    if not openai_model:
        raise ValueError("MODEL NOT FOUND")
except Exception as e:
    print(f"ERROR: {e}")
    openai_api_key, openai_model = None, None

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.message import add_messages
from typing import Annotated, Literal, TypedDict
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

llm = ChatOpenAI(model = openai_model, openai_api_key = openai_api_key)

def callModel(state: MessagesState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {'messages': [response]}

graph = StateGraph(MessagesState)
graph.add_node("chatbot", callModel)
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)
app = graph.compile()

response = app.invoke({'messages': 'Hi, there! My name is User'})

print(response['messages'][1].content)