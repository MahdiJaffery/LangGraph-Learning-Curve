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

@tool
def search(query: str):
    """blablabla"""
    if 'lhe' in query.lower() or 'lahore' in query.lower():
        return "LAHORE MENTIONED RAAAAHHHHHHH🗣️🗣️🗣️🗣️🗣️🗣️"
    return "Sai kehta hai Shehzaday. Khush reh"

tools = [search]

tool_node = ToolNode(tools)

llmWithTool = llm.bind_tools(tools)

def callModel(state: MessagesState):
    messages = state['messages']
    response = llmWithTool.invoke(messages)
    return {'messages': [response]}

def routerFunction(state: MessagesState) -> Literal["tools", END]:
    messages = state["messages"]
    lastMessage = messages[-1]

    if lastMessage.tool_calls:
        return "tools"
    return END

graph = StateGraph(MessagesState)

graph.add_node("agent", callModel)
graph.add_node("tools", tool_node)

graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", routerFunction, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")

app = graph.compile()

app.invoke({'messages': "Hi, there! How are you today?"})

for output in app.stream({'messages': "Lahore?"}):
    for key, value in output.items():
        print("*"*10)
        print(f"Value at {key}: {value['messages'][0].content}")
        print("\n")

    