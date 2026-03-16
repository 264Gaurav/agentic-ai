import dagshub
import mlflow

dagshub.init(repo_owner='264Gaurav', repo_name='agentic-ai', mlflow=True)
mlflow.set_experiment("agent-3")
from typing import List, TypedDict


from langchain_core.messages import BaseMessage, ToolMessage, HumanMessage
from langgraph.graph import END, START, StateGraph

from chains import revisor_chain, first_responder_chain
from execute_tools import execute_tools

# Define state schema for the graph
class GraphState(TypedDict):
    messages: List[BaseMessage]

MAX_ITERATIONS = 2

# Create StateGraph with state schema
graph = StateGraph(GraphState)

# Node functions that work with state
def draft_node(state: GraphState):
    """Generate initial draft answer with reflection and search queries."""
    result = first_responder_chain.invoke({"messages": state["messages"]})
    return {"messages": state["messages"] + [result]}

def execute_tools_node(state: GraphState):
    """Execute search tools based on tool calls."""
    tool_messages = execute_tools(state["messages"])
    return {"messages": state["messages"] + tool_messages}

def revisor_node(state: GraphState):
    """Revise the answer based on search results and reflection."""
    result = revisor_chain.invoke({"messages": state["messages"]})
    return {"messages": state["messages"] + [result]}

# Add nodes to the graph
graph.add_node("draft", draft_node)
graph.add_node("execute_tools", execute_tools_node)
graph.add_node("revisor", revisor_node)

# Add edges
graph.add_edge(START, "draft")
graph.add_edge("draft", "execute_tools")
graph.add_edge("execute_tools", "revisor")

def event_loop(state: GraphState) -> str:
    """Determine if we should continue iterating or end."""
    count_tool_visits = sum(isinstance(item, ToolMessage) for item in state["messages"])
    num_iterations = count_tool_visits
    if num_iterations >= MAX_ITERATIONS:
        return END
    return "execute_tools"

graph.add_conditional_edges("revisor", event_loop)

app = graph.compile()

print(app.get_graph().draw_mermaid())

# Invoke with proper state format
question = "What are the current news on USA and Iran war for this week?"

with mlflow.start_run(run_name="news_qa"):
    mlflow.log_param("question", question)
    mlflow.log_param("max_iterations", MAX_ITERATIONS)

    response = app.invoke({
        "messages": [HumanMessage(content=question)]
    })

    final_messages = response["messages"]
    num_messages = len(final_messages)
    num_tool_messages = sum(isinstance(m, ToolMessage) for m in final_messages)

    mlflow.log_metric("num_messages", num_messages)
    mlflow.log_metric("num_tool_messages", num_tool_messages)

    # existing printing logic...
    for msg in reversed(final_messages):
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            tool_call = msg.tool_calls[0]
            if "args" in tool_call and "answer" in tool_call["args"]:
                answer = tool_call["args"]["answer"]
                mlflow.log_param("answer_preview", answer)
                print("\n=== Final Answer ===")
                print(answer)
                if "references" in tool_call["args"]:
                    print("\n=== References ===")
                    for ref in tool_call["args"]["references"]:
                        print(f"- {ref}")
                break