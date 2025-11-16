# LangGraph: Complete Guide to Building Stateful AI Applications

LangGraph is a framework for building stateful, multi-actor applications with LLMs. It provides a graph-based approach to orchestrating complex workflows, making it ideal for building sophisticated AI agents and applications.

---

## 📖 Table of Contents

1. [What is LangGraph?](#what-is-langgraph)
2. [Core Concepts](#core-concepts)
3. [Key Components](#key-components)
4. [Architecture & Flow](#architecture--flow)
5. [Key Techniques](#key-techniques)
6. [Important Features](#important-features)
7. [Getting Started](#getting-started)
8. [Common Patterns](#common-patterns)
9. [Best Practices](#best-practices)
10. [Advanced Topics](#advanced-topics)

---

## 🎯 What is LangGraph?

### Definition

**LangGraph** is a library for building stateful, multi-actor applications with LLMs. It extends LangChain by adding:

- **State Management**: Persistent state across steps
- **Graph-Based Workflows**: Visual, declarative workflow definition
- **Conditional Logic**: Dynamic routing based on state
- **Loops & Cycles**: Iterative processes
- **Human-in-the-Loop**: Built-in support for human feedback

### Why LangGraph?

**Problem with Simple Chains:**
```
Chain: A → B → C
- No state persistence
- No conditional logic
- No loops
- Linear only
```

**Solution with LangGraph:**
```
Graph: A → [Condition] → B or C → [Loop] → A
- State persists
- Conditional routing
- Loops and cycles
- Complex workflows
```

### When to Use LangGraph

✅ **Use LangGraph when:**
- You need state persistence across steps
- Your workflow has conditional logic
- You need iterative refinement
- You want visual workflow representation
- You need complex multi-step processes
- You want human-in-the-loop capabilities

❌ **Don't use LangGraph when:**
- Simple linear chains are sufficient
- No state management needed
- One-shot operations
- Performance is critical (overhead exists)

---

## 🧩 Core Concepts

### 1. State

**State** is the data that flows through your graph. It persists across all nodes and can be updated at any point.

```python
from typing import TypedDict, List
from langchain_core.messages import BaseMessage

class GraphState(TypedDict):
    messages: List[BaseMessage]  # Conversation history
    step_count: int              # Counter
    metadata: dict                # Additional data
```

**Key Points:**
- State is defined using `TypedDict` for type safety
- State is passed to every node
- Nodes return state updates (merged automatically)
- State persists throughout graph execution

### 2. Nodes

**Nodes** are functions that process state. Each node:
- Receives the current state
- Performs some operation
- Returns state updates

```python
def my_node(state: GraphState):
    # Read from state
    messages = state["messages"]
    
    # Process
    result = do_something(messages)
    
    # Return state update
    return {"messages": state["messages"] + [result]}
```

**Node Characteristics:**
- Can be any Python function
- Receives full state
- Returns partial state (only what changed)
- State updates are merged automatically

### 3. Edges

**Edges** define how data flows between nodes. There are three types:

#### a) Fixed Edges
Always follow the same path.

```python
graph.add_edge(START, "node_a")
graph.add_edge("node_a", "node_b")
graph.add_edge("node_b", END)
```

#### b) Conditional Edges
Route based on a function's return value.

```python
def should_continue(state: GraphState):
    if state["step_count"] > 5:
        return "end"
    return "continue"

graph.add_conditional_edges("node_a", should_continue)
```

#### c) Entry/Exit Points
Special nodes: `START` and `END`

```python
graph.add_edge(START, "first_node")
graph.add_edge("last_node", END)
```

### 4. Graph

The **Graph** is the overall structure that connects nodes with edges.

```python
from langgraph.graph import StateGraph, START, END

graph = StateGraph(GraphState)
graph.add_node("node_a", node_a_function)
graph.add_edge(START, "node_a")
graph.add_edge("node_a", END)
app = graph.compile()
```

---

## 🔧 Key Components

### 1. StateGraph

The main class for creating stateful graphs.

```python
from langgraph.graph import StateGraph

graph = StateGraph(GraphState)
```

**Purpose:**
- Manages state structure
- Coordinates node execution
- Handles state updates

### 2. START and END

Special constants representing entry and exit points.

```python
from langgraph.graph import START, END

graph.add_edge(START, "first_node")
graph.add_edge("last_node", END)
```

### 3. Node Functions

Functions that process state.

```python
def process_node(state: GraphState):
    # Your logic here
    return {"key": "value"}  # State update
```

**Requirements:**
- Accept state as parameter
- Return dictionary with state updates
- Can be async or sync

### 4. Conditional Functions

Functions that determine routing.

```python
def route_decision(state: GraphState) -> str:
    if condition:
        return "path_a"
    return "path_b"
```

**Requirements:**
- Accept state as parameter
- Return string (node name) or `END`
- Must return valid node name

### 5. Compiled Graph (App)

The executable version of your graph.

```python
app = graph.compile()
result = app.invoke(initial_state)
```

**Capabilities:**
- Execution
- Visualization
- Streaming
- Persistence

---

## 🏗️ Architecture & Flow

### Basic Architecture

```
┌─────────────────────────────────────────┐
│         Initial State                   │
│  {"messages": [...], "step": 0}        │
└─────────────────────────────────────────┘
                    ↓
            ┌───────────────┐
            │     START      │
            └───────────────┘
                    ↓
        ┌───────────────────────┐
        │    Node A (Process)    │
        │  - Reads state         │
        │  - Updates state       │
        └───────────────────────┘
                    ↓
        ┌───────────────────────┐
        │ Conditional Edge      │
        │  - Evaluates state    │
        │  - Routes to next     │
        └───────────────────────┘
            ↙              ↘
    ┌──────────┐      ┌──────────┐
    │  Node B  │      │  Node C  │
    └──────────┘      └──────────┘
            ↘              ↙
        ┌───────────────────────┐
        │    Node D (Merge)     │
        └───────────────────────┘
                    ↓
            ┌───────────────┐
            │      END       │
            └───────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Final State                     │
│  {"messages": [...], "step": 3}        │
└─────────────────────────────────────────┘
```

### State Flow

```
Initial State
    ↓
Node 1 receives state
    ↓
Node 1 processes
    ↓
Node 1 returns update: {"key": "value"}
    ↓
State merged: {original_state + update}
    ↓
Node 2 receives updated state
    ↓
... (continues)
```

### Execution Flow

1. **Compile**: Graph is compiled into executable app
2. **Invoke**: Initial state is provided
3. **Start**: Execution begins at START node
4. **Execute Nodes**: Each node processes state
5. **Update State**: State is merged after each node
6. **Route**: Edges determine next node
7. **Repeat**: Until END is reached
8. **Return**: Final state is returned

---

## 🎨 Key Techniques

### 1. State Schema Definition

**Best Practice:** Use TypedDict for type safety

```python
from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage

class GraphState(TypedDict):
    messages: List[BaseMessage]
    step_count: int
    user_input: str
    result: Optional[str]
    metadata: dict
```

**Benefits:**
- Type checking
- IDE autocomplete
- Clear documentation
- Error prevention

### 2. State Updates

**Partial Updates:** Only return what changed

```python
def node_function(state: GraphState):
    # Good: Only return what changed
    return {"step_count": state["step_count"] + 1}
    
    # Bad: Returning full state (unnecessary)
    # return {"messages": [...], "step_count": ..., ...}
```

**State Merging:**
- LangGraph automatically merges updates
- New values overwrite old ones
- Lists/arrays are replaced (not merged)

### 3. Conditional Routing

**Simple Conditional:**

```python
def should_continue(state: GraphState) -> str:
    if len(state["messages"]) > 10:
        return END
    return "next_node"
```

**Complex Conditional:**

```python
def route_decision(state: GraphState) -> str:
    messages = state["messages"]
    last_message = messages[-1].content.lower()
    
    if "error" in last_message:
        return "error_handler"
    elif "retry" in last_message:
        return "retry_node"
    else:
        return "success_node"
```

### 4. Loops and Cycles

**Creating Loops:**

```python
# Node A → Node B → Node A (loop)
graph.add_edge("node_a", "node_b")
graph.add_edge("node_b", "node_a")

# Conditional loop
def should_loop(state: GraphState) -> str:
    if state["step_count"] < 5:
        return "node_a"  # Loop back
    return END
```

**Preventing Infinite Loops:**

```python
def should_continue(state: GraphState) -> str:
    # Safety check
    if state["step_count"] > 100:
        return END
    if state["error_count"] > 3:
        return END
    return "continue"
```

### 5. Node Composition

**Simple Node:**

```python
def simple_node(state: GraphState):
    return {"result": "done"}
```

**Complex Node with LLM:**

```python
def llm_node(state: GraphState):
    messages = state["messages"]
    result = llm.invoke(messages)
    return {"messages": state["messages"] + [result]}
```

**Node with Tool Calls:**

```python
def tool_node(state: GraphState):
    query = state["user_input"]
    result = search_tool.invoke(query)
    return {"search_results": result}
```

### 6. Error Handling

**Try-Except in Nodes:**

```python
def safe_node(state: GraphState):
    try:
        result = risky_operation(state)
        return {"result": result}
    except Exception as e:
        return {"error": str(e), "error_count": state.get("error_count", 0) + 1}
```

**Error Routing:**

```python
def route_with_error_handling(state: GraphState) -> str:
    if "error" in state:
        return "error_handler"
    return "normal_flow"
```

---

## ⭐ Important Features

### 1. Visualization

**Mermaid Diagram:**

```python
app = graph.compile()
print(app.get_graph().draw_mermaid())
```

**ASCII Visualization:**

```python
app.get_graph().print_ascii()
```

**Output Example:**
```
    START
      |
      v
  [GENERATE]
      |
      v
  [CONDITION]
   /     \
  v       v
[REFLECT] END
  |
  v
[GENERATE]
```

### 2. Streaming

**Stream Intermediate Steps:**

```python
for event in app.stream(initial_state):
    print(f"Node: {event}")
    print(f"State: {event.get('state', {})}")
```

**Benefits:**
- Real-time updates
- Progress tracking
- Debugging
- User feedback

### 3. Persistence

**Save Checkpoints:**

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
app = graph.compile(checkpointer=memory)

# Save state
config = {"configurable": {"thread_id": "1"}}
app.invoke(initial_state, config=config)

# Resume later
app.invoke(None, config=config)  # Continues from saved state
```

**Use Cases:**
- Long-running processes
- Human-in-the-loop
- Resume after interruption
- State inspection

### 4. Human-in-the-Loop

**Interrupt for Human Input:**

```python
from langgraph.graph import interrupt

def human_review_node(state: GraphState):
    # Process
    result = generate_content(state)
    
    # Wait for human approval
    interrupt()  # Pauses execution
    
    return {"result": result}
```

**Benefits:**
- Quality control
- Approval workflows
- Human oversight
- Interactive processes

### 5. Parallel Execution

**Multiple Paths:**

```python
# Node A branches to B and C (parallel)
graph.add_edge("node_a", "node_b")
graph.add_edge("node_a", "node_c")

# Both B and C must complete before D
graph.add_edge("node_b", "node_d")
graph.add_edge("node_c", "node_d")
```

### 6. State Inspection

**Access State at Any Point:**

```python
def debug_node(state: GraphState):
    print(f"Current state: {state}")
    print(f"Messages: {len(state['messages'])}")
    print(f"Step: {state['step_count']}")
    return {}
```

---

## 🚀 Getting Started

### Step 1: Installation

```bash
pip install langgraph
```

### Step 2: Define State

```python
from typing import TypedDict, List
from langchain_core.messages import BaseMessage

class GraphState(TypedDict):
    messages: List[BaseMessage]
```

### Step 3: Create Graph

```python
from langgraph.graph import StateGraph, START, END

graph = StateGraph(GraphState)
```

### Step 4: Define Nodes

```python
def node_a(state: GraphState):
    # Your logic
    return {"messages": state["messages"] + [new_message]}
```

### Step 5: Add Nodes

```python
graph.add_node("node_a", node_a)
```

### Step 6: Add Edges

```python
graph.add_edge(START, "node_a")
graph.add_edge("node_a", END)
```

### Step 7: Compile

```python
app = graph.compile()
```

### Step 8: Execute

```python
initial_state = {"messages": [HumanMessage(content="Hello")]}
result = app.invoke(initial_state)
```

### Complete Example

```python
from typing import TypedDict, List
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

# 1. Define State
class GraphState(TypedDict):
    messages: List[BaseMessage]

# 2. Create Graph
graph = StateGraph(GraphState)

# 3. Define Nodes
def process_node(state: GraphState):
    last_message = state["messages"][-1].content
    response = f"Processed: {last_message}"
    return {"messages": state["messages"] + [HumanMessage(content=response)]}

# 4. Add Nodes
graph.add_node("process", process_node)

# 5. Add Edges
graph.add_edge(START, "process")
graph.add_edge("process", END)

# 6. Compile
app = graph.compile()

# 7. Execute
result = app.invoke({
    "messages": [HumanMessage(content="Hello, LangGraph!")]
})

print(result)
```

---

## 📋 Common Patterns

### Pattern 1: Linear Flow

```
START → A → B → C → END
```

```python
graph.add_edge(START, "a")
graph.add_edge("a", "b")
graph.add_edge("b", "c")
graph.add_edge("c", END)
```

### Pattern 2: Conditional Branching

```
START → A → [Condition] → B or C → END
```

```python
def route(state: GraphState) -> str:
    return "b" if condition else "c"

graph.add_edge(START, "a")
graph.add_conditional_edges("a", route)
graph.add_edge("b", END)
graph.add_edge("c", END)
```

### Pattern 3: Loop

```
START → A → B → [Continue?] → A or END
```

```python
def should_continue(state: GraphState) -> str:
    return "a" if state["step"] < 5 else END

graph.add_edge(START, "a")
graph.add_edge("a", "b")
graph.add_conditional_edges("b", should_continue)
```

### Pattern 4: Generate-Reflect Loop

```
START → GENERATE → [Check] → REFLECT → GENERATE → END
```

```python
def should_reflect(state: GraphState) -> str:
    if len(state["messages"]) > 4:
        return END
    return "reflect"

graph.add_edge(START, "generate")
graph.add_conditional_edges("generate", should_reflect)
graph.add_edge("reflect", "generate")
```

### Pattern 5: Parallel Processing

```
START → A → [B, C] → D → END
```

```python
graph.add_edge(START, "a")
graph.add_edge("a", "b")
graph.add_edge("a", "c")
graph.add_edge("b", "d")
graph.add_edge("c", "d")
graph.add_edge("d", END)
```

### Pattern 6: Error Handling

```
START → A → [Success/Error] → B or ERROR_HANDLER → END
```

```python
def route(state: GraphState) -> str:
    if "error" in state:
        return "error_handler"
    return "b"

graph.add_edge(START, "a")
graph.add_conditional_edges("a", route)
graph.add_edge("b", END)
graph.add_edge("error_handler", END)
```

---

## 💡 Best Practices

### 1. State Design

**✅ Good:**
```python
class GraphState(TypedDict):
    messages: List[BaseMessage]
    step_count: int
    user_input: str
```

**❌ Bad:**
```python
class GraphState(TypedDict):
    everything: dict  # Too vague
    data: Any         # No type safety
```

### 2. Node Functions

**✅ Good:**
```python
def clear_node(state: GraphState):
    # Single responsibility
    return {"step_count": 0}
```

**❌ Bad:**
```python
def do_everything_node(state: GraphState):
    # Too many responsibilities
    result1 = do_this(state)
    result2 = do_that(state)
    result3 = do_other(state)
    return {"r1": result1, "r2": result2, "r3": result3}
```

### 3. State Updates

**✅ Good:**
```python
def node(state: GraphState):
    return {"step_count": state["step_count"] + 1}  # Only what changed
```

**❌ Bad:**
```python
def node(state: GraphState):
    return state  # Returning everything (inefficient)
```

### 4. Error Handling

**✅ Good:**
```python
def safe_node(state: GraphState):
    try:
        result = risky_operation()
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}
```

**❌ Bad:**
```python
def unsafe_node(state: GraphState):
    result = risky_operation()  # No error handling
    return {"result": result}
```

### 5. Conditional Logic

**✅ Good:**
```python
def clear_route(state: GraphState) -> str:
    if state["step_count"] > 10:
        return END
    return "next"
```

**❌ Bad:**
```python
def confusing_route(state: GraphState) -> str:
    # Complex nested logic
    if condition1:
        if condition2:
            if condition3:
                return "a"
            return "b"
        return "c"
    return "d"
```

### 6. Documentation

**✅ Good:**
```python
def process_node(state: GraphState):
    """
    Processes user input and generates response.
    
    Args:
        state: Current graph state
        
    Returns:
        State update with new message
    """
    # Implementation
```

**❌ Bad:**
```python
def node(state):  # No documentation
    # Implementation
```

---

## 🔬 Advanced Topics

### 1. Async Nodes

```python
async def async_node(state: GraphState):
    result = await async_operation()
    return {"result": result}
```

### 2. State Reducers

Custom state merging logic:

```python
def custom_reducer(current: dict, update: dict) -> dict:
    # Custom merge logic
    merged = current.copy()
    merged.update(update)
    if "messages" in merged:
        merged["messages"] = current["messages"] + update["messages"]
    return merged
```

### 3. Subgraphs

Nested graphs:

```python
subgraph = StateGraph(SubState)
# ... build subgraph ...

def node_with_subgraph(state: GraphState):
    result = subgraph_app.invoke(state["sub_state"])
    return {"result": result}
```

### 4. Dynamic Node Addition

```python
def add_node_dynamically(graph, node_name, node_func):
    graph.add_node(node_name, node_func)
```

### 5. State Validation

```python
def validate_state(state: GraphState):
    assert "messages" in state
    assert isinstance(state["messages"], list)
    return state
```

---

## 📊 Real-World Example: Reflection Agent

Let's analyze the reflection agent from this project:

```python
# State Definition
class GraphState(TypedDict):
    messages: List[BaseMessage]

# Graph Creation
graph = StateGraph(GraphState)

# Nodes
def generate_node(state: GraphState):
    result = generation_chain.invoke({"messages": state["messages"]})
    return {"messages": state["messages"] + [result]}

def reflect_node(state: GraphState):
    response = reflection_chain.invoke({"messages": state["messages"]})
    return {"messages": state["messages"] + [HumanMessage(content=response.content)]}

# Add Nodes
graph.add_node(GENERATE, generate_node)
graph.add_node(REFLECT, reflect_node)

# Conditional Logic
def should_continue(state: GraphState):
    if len(state["messages"]) > 4:
        return END
    return REFLECT

# Edges
graph.add_edge(START, GENERATE)
graph.add_conditional_edges(GENERATE, should_continue)
graph.add_edge(REFLECT, GENERATE)

# Compile & Execute
app = graph.compile()
result = app.invoke({"messages": [HumanMessage(content="Topic")]})
```

**Flow:**
1. Start with user message
2. Generate content
3. Check: if messages > 4, end; else reflect
4. Reflect on content
5. Loop back to generate (with feedback)
6. Repeat until condition met

---

## 🎓 Key Takeaways

1. **State is Central**: Everything revolves around state
2. **Nodes Process**: Nodes read and update state
3. **Edges Route**: Edges determine flow
4. **Graph Orchestrates**: Graph coordinates everything
5. **Visualize First**: Draw your workflow before coding
6. **Start Simple**: Begin with linear flow, add complexity
7. **Type Safety**: Use TypedDict for state
8. **Error Handling**: Always handle errors gracefully
9. **Documentation**: Document your nodes and state
10. **Test Incrementally**: Test each node independently

---

## 📚 Resources

- **Official Documentation**: [langchain-ai.github.io/langgraph](https://langchain-ai.github.io/langgraph/)
- **GitHub**: [github.com/langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)
- **Examples**: Check the examples directory in the repo
- **Community**: LangChain Discord server

---

## 🚀 Next Steps

1. **Start Simple**: Build a linear graph
2. **Add Conditionals**: Add routing logic
3. **Create Loops**: Implement iterative processes
4. **Add State**: Make it stateful
5. **Visualize**: Use visualization tools
6. **Optimize**: Refine your graph
7. **Deploy**: Put it in production

---

**Happy Graph Building! 🎉**

Remember: LangGraph is a powerful tool for building complex AI applications. Start simple, iterate, and gradually add complexity as needed!

