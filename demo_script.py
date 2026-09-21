import requests
import json
import time

API_URL = "http://localhost:8001/v1/tickets"

def print_result(response_data):
    print("--------------------------------------------------")
    print(f"Ticket ID: {response_data.get('ticket_id')}")
    print(f"Intent identified: {response_data.get('intent')}")
    print(f"Status: {response_data.get('status').upper()}")
    print(f"Confident: {response_data.get('is_confident')} | Safe: {response_data.get('is_safe')}")
    print("\nResolution Message:")
    print(response_data.get('resolution_message'))
    print("--------------------------------------------------\n")

def run_demo():
    print("Starting ResolveAI Demo...")
    # Wait a moment if the server just started
    time.sleep(2)

    tickets = [
        {
            "ticket_id": "T-001",
            "user_email": "customer@example.com",
            "issue_description": "Can you tell me where my order ORD-123 is? I ordered it last week."
        },
        {
            "ticket_id": "T-002",
            "user_email": "john.doe@example.com",
            "issue_description": "I forgot my password and can't log in."
        },
        {
            "ticket_id": "T-003",
            "user_email": "jane.smith@example.com",
            "issue_description": "I need to reset my password." # Account is locked in mock data
        },
        {
            "ticket_id": "T-004",
            "user_email": "angry.customer@example.com",
            "issue_description": "My laptop exploded and I want to sue you! I demand a refund for ORD-789."
        },
        {
            "ticket_id": "T-005",
            "user_email": "curious@example.com",
            "issue_description": "What is your return and refund policy? How long do I have to return something?"
        }
    ]

    for ticket in tickets:
        print(f"\nSending ticket {ticket['ticket_id']}...")
        try:
            response = requests.post(API_URL, json=ticket)
            response.raise_for_status()
            print_result(response.json())
        except requests.exceptions.RequestException as e:
            print(f"Error calling API: {e}")

if __name__ == "__main__":
    run_demo()
