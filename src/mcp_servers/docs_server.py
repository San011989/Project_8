from typing import Dict, Any, List

# Mock help articles / knowledge base
MOCK_DOCS = [
    {
        "id": "DOC-001",
        "title": "How to track your order",
        "tags": ["order", "tracking", "status", "shipment"],
        "content": (
            "You can track your order by logging into your account and visiting the 'My Orders' section. "
            "Orders typically take 2–5 business days to ship. Once shipped, a tracking number will be "
            "emailed to you. You can also use the order ID (e.g. ORD-123) to look up real-time status."
        ),
    },
    {
        "id": "DOC-002",
        "title": "How to request a refund",
        "tags": ["refund", "return", "money back", "cancel"],
        "content": (
            "Refunds are available within 30 days of purchase. To request a refund, contact our support "
            "team with your order ID and the reason for the refund. Refunds are processed within 5–7 "
            "business days back to the original payment method."
        ),
    },
    {
        "id": "DOC-003",
        "title": "How to reset your password",
        "tags": ["password", "reset", "login", "account", "forgot"],
        "content": (
            "To reset your password, click 'Forgot Password' on the login page and enter your registered "
            "email address. You will receive a password reset link within a few minutes. If you do not "
            "receive the email, check your spam folder or contact support."
        ),
    },
    {
        "id": "DOC-004",
        "title": "What to do if your account is locked",
        "tags": ["locked", "account", "blocked", "suspended", "access"],
        "content": (
            "Accounts can be locked after multiple failed login attempts or due to suspicious activity. "
            "To unlock your account, please contact our support team directly. An admin will verify your "
            "identity and restore access within 24 hours."
        ),
    },
    {
        "id": "DOC-005",
        "title": "Shipping and delivery policy",
        "tags": ["shipping", "delivery", "policy", "estimated", "time"],
        "content": (
            "Standard shipping takes 3–7 business days. Express shipping (1–2 business days) is available "
            "for an additional fee. We ship to most countries worldwide. Shipping costs are calculated at "
            "checkout based on weight and destination."
        ),
    },
    {
        "id": "DOC-006",
        "title": "How to contact customer support",
        "tags": ["contact", "support", "help", "human", "agent", "chat"],
        "content": (
            "You can reach our customer support team via live chat on our website (available 9am–6pm EST), "
            "by emailing support@resolveai.com, or by calling 1-800-555-0199. For urgent issues, "
            "live chat is the fastest option."
        ),
    },
]


def search_docs(query: str) -> Dict[str, Any]:
    """
    Search the help documentation / knowledge base for articles matching a query.

    Args:
        query: A search term or phrase describing what the user needs help with
               (e.g. 'how to get a refund', 'reset password', 'track my order').

    Returns:
        A dict with a list of matching help articles (title + content snippet).
    """
    query_lower = query.lower()
    query_words = set(query_lower.split())

    scored: List[Dict[str, Any]] = []
    for doc in MOCK_DOCS:
        # Score by tag overlap and keyword presence in title/content
        tag_hits = sum(1 for tag in doc["tags"] if tag in query_lower)
        title_hits = sum(1 for word in query_words if word in doc["title"].lower())
        content_hits = sum(1 for word in query_words if word in doc["content"].lower())
        score = tag_hits * 3 + title_hits * 2 + content_hits

        if score > 0:
            scored.append({"score": score, "doc": doc})

    scored.sort(key=lambda x: x["score"], reverse=True)
    top_results = scored[:3]  # Return top 3 matches

    if not top_results:
        return {
            "success": False,
            "message": f"No help articles found for query: '{query}'.",
            "results": [],
        }

    return {
        "success": True,
        "results": [
            {
                "id": r["doc"]["id"],
                "title": r["doc"]["title"],
                "snippet": r["doc"]["content"][:200] + "...",
            }
            for r in top_results
        ],
    }


# List of tools to be exposed to the agent
DOCS_TOOLS = [search_docs]
