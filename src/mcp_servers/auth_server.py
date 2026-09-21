from typing import Dict, Any

MOCK_USERS = {
    "john.doe@example.com": {"id": "U101", "name": "John Doe", "status": "active"},
    "jane.smith@example.com": {"id": "U102", "name": "Jane Smith", "status": "locked"}
}

def reset_password(email: str) -> Dict[str, Any]:
    """
    Send a password reset link to the user's email.
    
    Args:
        email: The email address of the user.
        
    Returns:
        Status of the password reset operation.
    """
    user = MOCK_USERS.get(email)
    if not user:
         return {"success": False, "error": f"User with email {email} not found."}
         
    if user["status"] == "locked":
         return {"success": False, "error": f"Account for {email} is locked. Password reset requires admin intervention."}
         
    return {"success": True, "message": f"Password reset link successfully sent to {email}."}

def check_account_status(email: str) -> Dict[str, Any]:
     """
     Check the status of a user account.
     
     Args:
        email: The email address of the user.
        
     Returns:
        Account status.
     """
     user = MOCK_USERS.get(email)
     if not user:
         return {"success": False, "error": f"User with email {email} not found."}
         
     return {"success": True, "status": user["status"]}

AUTH_TOOLS = [reset_password, check_account_status]
