# 🧠 LangGraph + OpenAI + Tools Integration

This project demonstrates how to build a conversational agent using LangGraph, LangChain, and OpenAI's GPT model, with tool use and memory checkpointing.

---
## 🎞️ Features

- ✅ Loads environment variables from a .env file

- ✅ Uses langchain-openai's ChatOpenAI LLM

- ✅ Supports tool calls (e.g., a custom search function)

- ✅ Streamable LangGraph workflows

- ✅ Memory-aware conversations using MemorySaver
---

## 🛠️ Setup
### 1. Install Dependencies
```
pip install -r requirements.txt
```
Minimum required packages:

```
python-dotenv
langchain
langchain-openai
langgraph
```

### 2. Create a .env file
```
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4o  # or gpt-4-turbo, gpt-3.5-turbo etc.
```
---
## 🧪 How It Works

### 🔧 Tool

A basic tool search() is defined to handle specific keywords (like “Lahore”).
```python
@tool
def search(query: str):
    if 'lahore' in query.lower():
        return "LAHORE MENTIONED RAAAAHHHHHHH🗣️🗣️"
    return "Sai kehta hai Shehzaday. Khush reh"
```
### 🧹 Graph Structure

The LangGraph defines the following nodes and flow:
```
graph TD
    START --> agent
    agent -->|tool_calls| tools
    agent -->|no tool_calls| END
    tools --> agent
```
- `agent`: The main LLM call

- `tools`: Executes tool invocations

- Loops back to agent if tools are used

### 🧠 Memory Integration

MemorySaver is used in graph2 to enable memory across multiple messages (e.g., remembering the user's name).
```python
config = {'configurable': {'thread_id': '1'}}
```

This lets the agent persist context across calls in a specific "thread".

---
## 🚀 Usage
```bash
python LangGraph.py
```

The script demonstrates:

- A simple one-off invoke using app

- A streamed response showing tool handling with app.stream(...)

- A memory-aware multi-turn conversation with app2 using checkpointing

### 🧠 Example Output

```bash
**********
Value at agent: LAHORE MENTIONED RAAAAHHHHHHH🗣️🗣️🗣️🗣️🗣️🗣️

User: Hi, there! My name is User. Could you tell me the weather in Lahore for today?
Assistant: LAHORE MENTIONED RAAAAHHHHHHH🗣️🗣️🗣️🗣️🗣️🗣️

User: What is my name again?
Assistant: Your name is User.
```

---
## 📁 File Structure
```
.
├── LangGraph.py       # Main execution script
├── requirements.txt   # Requirements listed
└── README.md          # You're reading this!
```
---
## 🧠 Notes

- Ensure your .env file exists and contains the correct keys.

- Change the search tool to integrate real APIs if needed (e.g., weather, search engines).

- Set unique thread_ids to isolate conversations.