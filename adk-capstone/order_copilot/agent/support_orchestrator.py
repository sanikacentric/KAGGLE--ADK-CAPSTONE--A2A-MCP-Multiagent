# order_copilot/agent/support_orchestrator.py

import os
import time
import uuid
from typing import Dict, Any, Optional

from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from google.adk.tools.function_tool import FunctionTool

# -----------------------------------------------------------------------------
# Model / retry config
# -----------------------------------------------------------------------------
api_key = os.getenv("GOOGLE_API_KEY")

TOOL_CONFIG = types.ToolConfig(
    function_calling_config=types.FunctionCallingConfig(mode="AUTO")
)

RETRY = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# -----------------------------------------------------------------------------
# In-memory state for the long-running scan demo
# -----------------------------------------------------------------------------
_PENDING: Dict[str, Dict[str, Any]] = {}
_LAST_TOKEN: Optional[str] = None


# -----------------------------------------------------------------------------
# Tool implementations (docstrings used by older ADK for name/description)
# -----------------------------------------------------------------------------
def _shipping_eta(zipcode: str) -> Dict[str, Any]:
    """shipping_eta: Return shipping ETA for a US zipcode. Output: {ok, message}."""
    z = (zipcode or "").strip()
    if not z.isdigit():
        return {"ok": False, "message": "Invalid zipcode."}
    days = 2 if z.startswith(("0", "1", "2", "3")) else 5
    return {"ok": True, "message": f"Estimated delivery: {days} business days."}


def _start_risk_scan(order_id: str) -> Dict[str, Any]:
    """start_risk_scan: Start a long-running risk scan. Output: {status, token}."""
    global _LAST_TOKEN
    token = str(uuid.uuid4())
    _PENDING[token] = {"order_id": order_id, "ready_at": time.time() + 3}
    _LAST_TOKEN = token
    return {"status": "STARTED", "token": token}


def _resume_risk_scan(token: str) -> Dict[str, Any]:
    """resume_risk_scan: Resume with token (or 'last'). Output: {status, order?, risk?, message?}."""
    global _LAST_TOKEN
    token = (token or "").strip()
    if token.lower() == "last":
        token = _LAST_TOKEN or ""
    if not token:
        return {"status": "ERROR", "message": "MISSING_TOKEN"}

    rec = _PENDING.get(token)
    if not rec:
        return {"status": "ERROR", "message": "NO_SUCH_TOKEN"}

    if time.time() < rec["ready_at"]:
        return {"status": "PENDING", "message": "NOT_READY"}

    _PENDING.pop(token, None)
    return {"status": "OK", "order": rec["order_id"], "risk": "LOW"}


def _mcp_fetch_file_note(filename: str) -> Dict[str, Any]:
    """mcp_fetch_file_note: Fetch a local note via MCP bridge. Output: {ok, content}."""
    return {"ok": True, "content": f"MCP(filesystem) read request for: {filename} (demo stub)"}


# -----------------------------------------------------------------------------
# Wrap functions as FunctionTool  (older ADK: positional only)
# -----------------------------------------------------------------------------
shipping_eta = FunctionTool(_shipping_eta)
start_risk_scan = FunctionTool(_start_risk_scan)
resume_risk_scan = FunctionTool(_resume_risk_scan)
mcp_fetch_file_note = FunctionTool(_mcp_fetch_file_note)

# -----------------------------------------------------------------------------
# Remote A2A sub-agents
# -----------------------------------------------------------------------------
CATALOG_BASE = os.getenv("CATALOG_BASE_URL", "http://localhost:8001")
COMPLIANCE_BASE = os.getenv("COMPLIANCE_BASE_URL", "http://localhost:8002")

catalog = RemoteA2aAgent(
    name="product_catalog_agent",
    description="Remote vendor catalog via A2A.",
    agent_card=f"{CATALOG_BASE}{AGENT_CARD_WELL_KNOWN_PATH}",
)

compliance = RemoteA2aAgent(
    name="compliance_agent",
    description="Remote vendor compliance via A2A.",
    agent_card=f"{COMPLIANCE_BASE}{AGENT_CARD_WELL_KNOWN_PATH}",
)

# -----------------------------------------------------------------------------
# Root agent
# -----------------------------------------------------------------------------
root_agent = LlmAgent(
    model=Gemini(
        model="gemini-2.5-flash-lite",
        api_key=api_key,
        retry_options=RETRY,
        tool_config=TOOL_CONFIG,
    ),
    name="support_orchestrator",
    description="Customer Support Copilot that orchestrates remote agents and tools.",
    instruction="""
You are a helpful support agent.

ROUTING:
- For product questions, delegate to product_catalog_agent.
- For compliance questions, delegate to compliance_agent.
- Use shipping_eta for delivery estimates.
- If user says "scan order <id>", call start_risk_scan and return the token.
- If user says "resume <token>" (or 'last'), call resume_risk_scan.
- If user asks to fetch a local note, use mcp_fetch_file_note.

VERY IMPORTANT (POST-TOOL BEHAVIOR):
After you call any tool or sub-agent and receive its result, WRITE A FINAL, NATURAL-LANGUAGE
ANSWER to the user that mentions which tool/agent you used. Do NOT call another tool in the
same turn unless the user provides new information. If a tool returns JSON, read it and explain
the important fields clearly.

Keep answers concise and helpful.
""",
    tools=[shipping_eta, start_risk_scan, resume_risk_scan, mcp_fetch_file_note],
    sub_agents=[catalog, compliance],
)
