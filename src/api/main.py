from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI, HTTPException
from src.api.models import TicketRequest, TicketResponse
from src.agent.graph import app as agent_app

app = FastAPI(title="ResolveAI", description="Autonomous Ticket Resolution Agent")

@app.get("/health")
def health_check():
    """Health check endpoint for load balancers and orchestrators."""
    return {"status": "healthy"}

@app.post("/v1/tickets", response_model=TicketResponse)
async def process_ticket(request: TicketRequest):
    """
    Process an incoming support ticket using the AI agent.
    """
    try:
        # Initialize state
        initial_state = {
            "ticket_id": request.ticket_id,
            "user_email": request.user_email,
            "issue_description": request.issue_description,
            "tool_results": []
        }
        
        # Run the agent graph
        result = agent_app.invoke(initial_state)
        
        return TicketResponse(
            ticket_id=request.ticket_id,
            status=result.get("resolution_status", "error"),
            resolution_message=result.get("resolution_message", "Failed to resolve or escalate properly."),
            intent=result.get("intent"),
            is_confident=result.get("is_confident"),
            is_safe=result.get("is_safe")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
