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
response = app.invoke({
    "messages": [HumanMessage(content="Write about how small business can leverage AI to grow")]
})

# Extract and print the final answer
final_messages = response["messages"]
# Find the last message with tool calls (should be the final answer)
for msg in reversed(final_messages):
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        tool_call = msg.tool_calls[0]
        if "args" in tool_call and "answer" in tool_call["args"]:
            print("\n=== Final Answer ===")
            print(tool_call["args"]["answer"])
            if "references" in tool_call["args"]:
                print("\n=== References ===")
                for ref in tool_call["args"]["references"]:
                    print(f"- {ref}")
            break