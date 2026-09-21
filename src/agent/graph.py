import json
import re
from typing import Literal
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from .state import TicketState
from .prompts import INTENT_CLASSIFICATION_PROMPT, PLANNER_PROMPT, EVALUATOR_PROMPT, RESPONDER_PROMPT
from src.mcp_servers.order_server import ORDER_TOOLS
from src.mcp_servers.auth_server import AUTH_TOOLS
from src.mcp_servers.docs_server import DOCS_TOOLS

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o")

# Map of tool names to actual functions for easy lookup
TOOL_MAP = {func.__name__: func for func in ORDER_TOOLS + AUTH_TOOLS + DOCS_TOOLS}

def understand_intent(state: TicketState) -> dict:
    """Node: Classifies the intent of the ticket."""
    prompt = INTENT_CLASSIFICATION_PROMPT.format(issue_description=state["issue_description"])
    response = llm.invoke([HumanMessage(content=prompt)])
    intent = response.content.strip()
    return {"intent": intent}

def make_plan(state: TicketState) -> dict:
    """Node: Creates a plan using available tools based on intent."""
    if state["intent"] == "unknown":
        return {"plan": []}
        
    prompt = PLANNER_PROMPT.format(
        intent=state["intent"],
        issue_description=state["issue_description"]
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        # Extract JSON list from response
        plan_text = response.content.strip()
        match = re.search(r'\[.*\]', plan_text, re.DOTALL)
        if match:
             plan = json.loads(match.group(0))
        else:
             plan = json.loads(plan_text)
    except Exception:
        plan = [] # Escalate on failure
    return {"plan": plan}

def extract_args_for_tool(tool_name: str, issue_description: str) -> dict:
    """Helper to extract arguments for a specific tool from the description."""
    prompt = f"Extract the arguments required for the tool '{tool_name}' from the text: '{issue_description}'.\n"
    if "order" in tool_name:
         prompt += "Return a JSON object with 'order_id' and if needed 'reason'."
    elif "auth" in tool_name or "password" in tool_name or "account" in tool_name:
         prompt += "Return a JSON object with 'email'."
    elif "doc" in tool_name or "search" in tool_name:
         prompt += "Return a JSON object with 'query' as a short search phrase."
    
    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        text = response.content.strip()
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
             return json.loads(match.group(0))
        return json.loads(text)
    except:
        return {}

def execute_tools(state: TicketState) -> dict:
    """Node: Executes the tools defined in the plan."""
    results = []
    for tool_name in state["plan"]:
        if tool_name in TOOL_MAP:
            tool_func = TOOL_MAP[tool_name]
            args = extract_args_for_tool(tool_name, state["issue_description"])
            try:
                # Call the actual mock MCP tool
                result = tool_func(**args)
                results.append({tool_name: result})
            except Exception as e:
                results.append({tool_name: {"success": False, "error": str(e)}})
        else:
            results.append({tool_name: {"success": False, "error": "Tool not found"}})
            
    return {"tool_results": results}

def evaluate_safety_and_confidence(state: TicketState) -> dict:
    """Node: Evaluates if it's safe to act and if agent is confident."""
    if not state["plan"]:
        return {"is_confident": False, "is_safe": False, "evaluation_reasoning": "No plan formulated, likely unknown intent."}
        
    prompt = EVALUATOR_PROMPT.format(
        issue_description=state["issue_description"],
        intent=state["intent"],
        plan=state["plan"],
        tool_results=state["tool_results"]
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        text = response.content.strip()
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
             eval_data = json.loads(match.group(0))
        else:
             eval_data = json.loads(text)
             
        return {
            "is_confident": eval_data.get("is_confident", False),
            "is_safe": eval_data.get("is_safe", False),
            "evaluation_reasoning": eval_data.get("reasoning", "Parsing failed")
        }
    except Exception:
         return {"is_confident": False, "is_safe": False, "evaluation_reasoning": "Evaluation output parsing failed."}

def decide_resolution(state: TicketState) -> Literal["resolve", "escalate"]:
    """Conditional edge logic."""
    if state["is_confident"] and state["is_safe"]:
        return "resolve"
    return "escalate"

def resolve_and_reply(state: TicketState) -> dict:
    """Node: Generates the final resolution message to the user."""
    prompt = RESPONDER_PROMPT.format(
        issue_description=state["issue_description"],
        tool_results=state["tool_results"],
        evaluation_reasoning=state["evaluation_reasoning"],
        resolution_status="resolved"
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"resolution_status": "resolved", "resolution_message": response.content.strip()}

def escalate_to_human(state: TicketState) -> dict:
    """Node: Generates the escalation summary and message."""
    prompt = RESPONDER_PROMPT.format(
        issue_description=state["issue_description"],
        tool_results=state["tool_results"],
        evaluation_reasoning=state["evaluation_reasoning"],
        resolution_status="escalated"
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"resolution_status": "escalated", "resolution_message": response.content.strip()}


# Build the graph
workflow = StateGraph(TicketState)

# Add nodes
workflow.add_node("understand_intent", understand_intent)
workflow.add_node("make_plan", make_plan)
workflow.add_node("execute_tools", execute_tools)
workflow.add_node("evaluate", evaluate_safety_and_confidence)
workflow.add_node("resolve", resolve_and_reply)
workflow.add_node("escalate", escalate_to_human)

# Add edges
workflow.add_edge(START, "understand_intent")
workflow.add_edge("understand_intent", "make_plan")
workflow.add_edge("make_plan", "execute_tools")
workflow.add_edge("execute_tools", "evaluate")

# Conditional routing after evaluation
workflow.add_conditional_edges(
    "evaluate",
    decide_resolution,
    {
        "resolve": "resolve",
        "escalate": "escalate"
    }
)

workflow.add_edge("resolve", END)
workflow.add_edge("escalate", END)

# Compile graph
app = workflow.compile()
