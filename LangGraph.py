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
from langchain_core.runnables import RunnableLambda
import operator

llm = ChatOpenAI(model = openai_model, openai_api_key = openai_api_key)

class MyState(TypedDict):
    messages: Annotated[list, operator.add]
    revision_count: int
    reflection_decision: str

@tool
def search(query: str):
    """blablabla"""
    if 'lhe' in query.lower() or 'lahore' in query.lower():
        return "LAHORE MENTIONED RAAAAHHHHHHH🗣️🗣️🗣️🗣️🗣️🗣️"
    return "Sai kehta hai Shehzaday. Khush reh"

tools = [search]

tool_node = ToolNode(tools)

llmWithTool = llm.bind_tools(tools)

def callModel(state: MyState):
    messages = state['messages']
    response = llmWithTool.invoke(messages)
    return {'messages': [response]}

def routerFunction(state: MyState) -> Literal["tools", END]:
    messages = state["messages"]
    lastMessage = messages[-1]

    if lastMessage.tool_calls:
        return "tools"
    return END

def post_reflection_router(state) -> Literal["agent", "tools", END]:
    decision = state.get("reflection_decision", "accept")

    if decision == 'revise':
        return 'agent'
    
    lastMessage = state['messages'][-1]
    if lastMessage.tool_calls:
        return 'tools'
    
    return END

def reflectionNode(state: MyState) -> dict:
    messages = state["messages"]
    last_message = messages[-1]

    if len(last_message.content.split()) < 5 or "I don't know" in last_message.content:
        print("Triggering Self-Reflection")
        return {'messages': messages, 'reflection_decision': "revise"}
    
    return {'messages': messages, 'reflection_decision': 'accept'}

def dynamic_reflection_node(state: MyState) -> dict:

    messages = state['messages']
    last_message = messages[-1]

    state['revision_count'] = state.get('revision_count', 0) + 1

    if state['revision_count'] > 2:
        return {'messages': messages, 'reflection_decision': 'accept', 'revision_count': state['revision_count']}

    print(f"IGNORE THIS LINE: {state['revision_count']}")

    reflectionPrompt = f"""You are a helpful and self-reflective assisstant. 
    Here is your most recent reply to a user: 
    
    "{last_message.content}"

    Was this response helpful and complete? Reply with "accept" or "revise".
    """

    decision_msg = llm.invoke([HumanMessage(content=reflectionPrompt)])

    decision = decision_msg.content.strip().lower()

    print(f"Reflection Decision: {decision}")

    if decision not in ["accept", "revise"]:
        decision = 'accept'

    return {'messages': messages, 'reflection_decision': decision, 'revision_count': state['revision_count']}
 

reflection = RunnableLambda(dynamic_reflection_node)


# graph = StateGraph(MyState)

# graph.add_node("agent", callModel)
# graph.add_node("tools", tool_node)

# graph.add_edge(START, "agent")
# graph.add_conditional_edges("agent", routerFunction, {"tools": "tools", END: END})
# graph.add_edge("tools", "agent")

# app = graph.compile()

# app.invoke({'messages': "Hi, there! How are you today?"})

# for output in app.stream({'messages': "Lahore?"}):
#     for key, value in output.items():
#         print("*"*10)
#         print(f"Value at {key}: {value['messages'][0].content}")
#         print("\n")

memory = MemorySaver()

# graph2 = StateGraph(MessagesState)

# graph2.add_node("agent", callModel)
# graph2.add_node("tools", tool_node)

# graph2.add_edge(START, "agent")
# graph2.add_conditional_edges("agent", routerFunction, {"tools": "tools", END: END})
# graph2.add_edge("tools", "agent")

# app2 = graph2.compile(checkpointer=memory)

graph2 = StateGraph(MyState)

graph2.add_node("agent", callModel)
graph2.add_node("tools", tool_node)
graph2.add_node('reflection', reflection)

graph2.set_entry_point("agent")

graph2.add_edge("agent", "reflection")

graph2.add_conditional_edges('reflection', post_reflection_router, {
    'agent':    'agent',
    'tools':    'tools',
    END: END
})

graph2.add_edge("tools", "agent")

app2 = graph2.compile(checkpointer=memory)

config = {'configurable': {'thread_id': '1'}}

# events = app2.stream({'messages': ['Hi, there! My name is User. Could you tell me the weather in Lahore for today?']}, config, stream_mode = "values")

# for event in events:
#     event['messages'][-1].pretty_print()

# events = app2.stream({'messages': ['What is my name again?']}, config, stream_mode="values")

# for event in events:
#     event['messages'][-1].pretty_print()


while True:

    inp = str(input("Prompt: "))

    if inp.lower() == 'q' or inp.lower() == 'quit':
        print("Exiting Chat...")
        break

    events = app2.stream({'messages': [HumanMessage(content = inp)]}, config, stream_mode="values")

    for event in events:
        event['messages'][-1].pretty_print()
