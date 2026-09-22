import requests
import time

API_URL = "http://resolveai-alb-1442038815.ap-south-1.elb.amazonaws.com/v1/tickets"

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
    print("Starting Live ResolveAI Demo (Single Ticket)...")
    
    ticket = {
        "ticket_id": "T-LIVE-001",
        "user_email": "customer@example.com",
        "issue_description": "Can you tell me where my order ORD-123 is? I ordered it last week."
    }

    print(f"\nSending ticket {ticket['ticket_id']} to live endpoint {API_URL}...")
    try:
        response = requests.post(API_URL, json=ticket)
        response.raise_for_status()
        print_result(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")

if __name__ == "__main__":
    run_demo()
