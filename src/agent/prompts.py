INTENT_CLASSIFICATION_PROMPT = """You are an AI support agent triage expert.
Your job is to identify the intent of the following support ticket.
Possible intents are:
- 'order_status_lookup': User wants to know the status of their order.
- 'refund_request': User is asking for a refund on an order.
- 'password_reset': User forgot their password and needs a reset.
- 'document_search': User is asking a general policy or how-to question (e.g. return policy, shipping times, how to contact support).
- 'unknown': The intent is not clear or does not match the above.

Ticket description:
{issue_description}

Respond with only the intent string.
"""

PLANNER_PROMPT = """You are an AI support agent planner.
Based on the ticket intent and description, create a step-by-step plan to resolve the issue using the available tools.
If the intent is 'unknown', the plan should be to escalate the ticket.

Intent: {intent}
Ticket description: {issue_description}

Available tools:
- lookup_order: Use when you need to find an order status. Requires order_id.
- process_refund: Use when you need to process a refund. Requires order_id and reason.
- reset_password: Use when you need to send a password reset link. Requires email.
- check_account_status: Use when you need to check a user's account status. Requires email.
- search_docs: Use when the user asks a general policy or how-to question (e.g. return policy, shipping info, contact support). Requires a query string.

Respond with a JSON list of tool names you plan to call, in order. Example: ["lookup_order", "process_refund"]
If escalating, respond with an empty list: []
"""

EVALUATOR_PROMPT = """You are a policy and safety evaluator for an autonomous AI support agent.
Review the original ticket, the plan, and the tool execution results.
Determine if the agent has enough confident information to resolve the ticket, and if the action taken (if any) was safe and compliant with policy.

Ticket: {issue_description}
Intent: {intent}
Plan: {plan}
Tool Results: {tool_results}

Respond in JSON format with the following keys:
- "is_confident": boolean (True if facts gathered are sufficient and clear)
- "is_safe": boolean (True if the action is allowed, e.g., refunds only for valid orders, password resets only for non-locked accounts)
- "reasoning": string (explanation of the decision)
"""

RESPONDER_PROMPT = """You are an AI support agent communicating with a user.
Based on the evaluation and tool results, formulate a final reply to the user.

Ticket: {issue_description}
Tool Results: {tool_results}
Evaluation Reasoning: {evaluation_reasoning}
Resolution Status: {resolution_status} (If 'resolved', formulate a helpful reply. If 'escalated', politely inform the user that their ticket has been escalated to a human agent along with a summary of the issue).

Write the final message to the user.
"""
