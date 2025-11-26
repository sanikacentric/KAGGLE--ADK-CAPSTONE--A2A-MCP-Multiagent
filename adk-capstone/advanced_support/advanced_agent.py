import os
from typing import Dict, Any
from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools.function_tool import FunctionTool

# Import the existing agent to be validated
# Assuming the project root is in PYTHONPATH
try:
    from order_copilot.agent.root_agent import root_agent as inner_agent
except ImportError:
    # Fallback for when running directly from root
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from order_copilot.agent.root_agent import root_agent as inner_agent

# -----------------------------------------------------------------------------
# Tools for the Advanced Agent
# -----------------------------------------------------------------------------

def _notify_customer_support(reason: str) -> Dict[str, Any]:
    """
    notify_customer_support: Notify human support when the inner agent fails or acts incorrectly.
    Args:
        reason: The reason for notification (e.g., "Agent hallucinated", "Incorrect shipping info").
    """
    print(f"\n[ALERT] NOTIFYING CUSTOMER SUPPORT: {reason}\n")
    return {"status": "NOTIFIED", "message": f"Support notified for reason: {reason}"}

notify_customer_support = FunctionTool(_notify_customer_support)

# -----------------------------------------------------------------------------
# Advanced Support Agent
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

advanced_agent = LlmAgent(
    model=Gemini(
        model="gemini-3.0-pro-001",
        api_key=api_key,
        retry_options=RETRY,
        tool_config=TOOL_CONFIG,
    ),
    name="advanced_support_validator",
    description="A supervisor agent that validates the output of the support_orchestrator.",
    instruction="""
You are an Advanced Support Supervisor. Your goal is to ensure the `support_orchestrator` agent is performing correctly.

PROTOCOL:
1. You will receive a user query.
2. You MUST delegate this query to the `support_orchestrator` sub-agent.
3. Analyze the response from `support_orchestrator`.
4. VALIDATION:
    - Did the agent answer the user's question?
    - Did the agent use the correct tools (e.g., shipping_eta for shipping)?
    - Is the answer reasonable and polite?
5. ACTION:
    - IF the response is CORRECT: Return the response to the user exactly as is (or slightly improved).
    - IF the response is INCORRECT, HALLUCINATED, or HARMFUL:
        a. Call `notify_customer_support` with the specific reason.
        b. Apologize to the user and provide the correct information if you know it, or say you have escalated the issue.

You have access to the `support_orchestrator` as a sub-agent. Use it to get the initial answer.
""",
    tools=[notify_customer_support],
    sub_agents=[inner_agent],
)
