# -*- coding: utf-8 -*-
"""
AI Agent Evaluation Suite.
Runs deterministic checks against the agent's MCP tools to verify
the pipeline works end-to-end before deployment.
Does NOT require a live OpenAI key -- tests tool logic directly.
"""
import sys
from src.mcp_servers.order_server import lookup_order, process_refund
from src.mcp_servers.auth_server import reset_password, check_account_status
from src.mcp_servers.docs_server import search_docs

PASS = "[PASS]"
FAIL = "[FAIL]"
results = []

def check(name, condition):
    status = PASS if condition else FAIL
    print("  {}  {}".format(status, name))
    results.append(condition)

print("\n[AI EVALS] ResolveAI - Agent Evaluation Suite")
print("=" * 50)

# Eval 1: Order intent toolchain
print("\n[Eval 1] Order status lookup tool")
r = lookup_order("ORD-123")
check("Returns success=True for valid order", r["success"] is True)
check("Returns order status field", "status" in r.get("order", {}))

# Eval 2: Refund toolchain
print("\n[Eval 2] Refund processing tool")
r = process_refund("ORD-789", reason="Defective product")
check("Returns success=True for valid order", r["success"] is True)
check("Confirms refund in message", "refund" in r.get("message", "").lower())

# Eval 3: Auth toolchain
print("\n[Eval 3] Password reset tool")
r = reset_password("john.doe@example.com")
check("Returns success=True for active account", r["success"] is True)

r_locked = reset_password("jane.smith@example.com")
check("Rejects locked account (safety check)", r_locked["success"] is False)

# Eval 4: Document search toolchain
print("\n[Eval 4] Document search tool")
r = search_docs("how to get a refund return policy")
check("Returns success=True for valid query", r["success"] is True)
check("Returns at least 1 result", len(r.get("results", [])) >= 1)
check("Results contain title and snippet", "title" in r["results"][0] and "snippet" in r["results"][0])

# Eval 5: Safety / escalation logic
print("\n[Eval 5] Escalation safety - locked account should not be auto-resolved")
r_status = check_account_status("jane.smith@example.com")
check("Account status returns 'locked'", r_status.get("status") == "locked")
r_fail = reset_password("jane.smith@example.com")
check("System refuses password reset on locked account", r_fail["success"] is False)

# Summary
print("\n" + "=" * 50)
passed = sum(results)
total = len(results)
print("Results: {}/{} checks passed".format(passed, total))

if passed < total:
    print("[BLOCKED] Some evals failed. Blocking deployment.")
    sys.exit(1)
else:
    print("[OK] All evals passed. Safe to build and deploy.")
    sys.exit(0)
