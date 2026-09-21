from typing import TypedDict, Annotated, List, Any, Dict
import operator

class TicketState(TypedDict):
    ticket_id: str
    user_email: str
    issue_description: str
    
    intent: str
    plan: List[str]
    
    # Store tool execution results
    tool_results: Annotated[List[Dict[str, Any]], operator.add]
    
    # Confidence and Policy Evaluation
    is_confident: bool
    is_safe: bool
    evaluation_reasoning: str
    
    # Final resolution
    resolution_status: str # "resolved" or "escalated"
    resolution_message: str
