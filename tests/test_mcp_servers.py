"""
Unit tests for ResolveAI MCP server tools.
These tests run without a live API key — they test mock data logic only.
"""
import pytest
from src.mcp_servers.order_server import lookup_order, process_refund
from src.mcp_servers.auth_server import reset_password, check_account_status
from src.mcp_servers.docs_server import search_docs


# ── Order Server Tests ────────────────────────────────────────────────────────

def test_lookup_order_found():
    result = lookup_order("ORD-123")
    assert result["success"] is True
    assert result["order"]["status"] == "shipped"

def test_lookup_order_not_found():
    result = lookup_order("ORD-FAKE")
    assert result["success"] is False
    assert "not found" in result["error"]

def test_process_refund_success():
    result = process_refund("ORD-456", reason="Item not as described")
    assert result["success"] is True
    assert "refunded" in result["message"].lower()

def test_process_refund_already_refunded():
    # ORD-456 was refunded in previous test (in-memory state)
    result = process_refund("ORD-456", reason="Duplicate request")
    assert result["success"] is False
    assert "already been refunded" in result["error"]

def test_process_refund_order_not_found():
    result = process_refund("ORD-FAKE", reason="test")
    assert result["success"] is False


# ── Auth Server Tests ─────────────────────────────────────────────────────────

def test_reset_password_success():
    result = reset_password("john.doe@example.com")
    assert result["success"] is True
    assert "reset link" in result["message"].lower()

def test_reset_password_locked_account():
    result = reset_password("jane.smith@example.com")
    assert result["success"] is False
    assert "locked" in result["error"].lower()

def test_reset_password_user_not_found():
    result = reset_password("nobody@example.com")
    assert result["success"] is False

def test_check_account_status_active():
    result = check_account_status("john.doe@example.com")
    assert result["success"] is True
    assert result["status"] == "active"

def test_check_account_status_locked():
    result = check_account_status("jane.smith@example.com")
    assert result["success"] is True
    assert result["status"] == "locked"


# ── Docs Server Tests ─────────────────────────────────────────────────────────

def test_search_docs_refund_policy():
    result = search_docs("refund policy return")
    assert result["success"] is True
    assert len(result["results"]) > 0
    titles = [r["title"].lower() for r in result["results"]]
    assert any("refund" in t for t in titles)

def test_search_docs_password():
    result = search_docs("reset password forgot login")
    assert result["success"] is True
    assert len(result["results"]) > 0

def test_search_docs_no_match():
    result = search_docs("xyzzy unrecognisable gibberish query")
    assert result["success"] is False
    assert result["results"] == []
