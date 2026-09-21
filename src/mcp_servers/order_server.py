from typing import Dict, Any, Optional

# Mock database
MOCK_ORDERS = {
    "ORD-123": {"status": "shipped", "amount": 120.50, "items": ["Wireless Mouse", "Keyboard"]},
    "ORD-456": {"status": "processing", "amount": 45.00, "items": ["USB-C Cable"]},
    "ORD-789": {"status": "delivered", "amount": 299.99, "items": ["Monitor"]}
}

MOCK_REFUNDS = {}

def lookup_order(order_id: str) -> Dict[str, Any]:
    """
    Look up an order by its ID.
    
    Args:
        order_id: The ID of the order to look up (e.g., 'ORD-123')
        
    Returns:
        Order details if found, else an error message.
    """
    order = MOCK_ORDERS.get(order_id)
    if order:
        return {"success": True, "order": order}
    return {"success": False, "error": f"Order {order_id} not found."}

def process_refund(order_id: str, reason: str) -> Dict[str, Any]:
    """
    Process a refund for a given order.
    
    Args:
        order_id: The ID of the order to refund.
        reason: The reason for the refund.
        
    Returns:
        Result of the refund operation.
    """
    order = MOCK_ORDERS.get(order_id)
    if not order:
        return {"success": False, "error": f"Order {order_id} not found. Cannot process refund."}
    
    if order["status"] == "refunded":
        return {"success": False, "error": f"Order {order_id} has already been refunded."}
        
    # Process refund
    MOCK_ORDERS[order_id]["status"] = "refunded"
    MOCK_REFUNDS[order_id] = {"amount": order["amount"], "reason": reason}
    
    return {"success": True, "message": f"Successfully refunded ${order['amount']} for order {order_id}."}

# List of tools to be exposed to the agent
ORDER_TOOLS = [lookup_order, process_refund]
