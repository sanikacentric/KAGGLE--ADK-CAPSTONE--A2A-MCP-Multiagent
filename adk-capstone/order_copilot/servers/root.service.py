# order_copilot/servers/root_service.py
import os
from fastapi import FastAPI
from pydantic import BaseModel
from google.adk.agents.runner import AgentRunner
from order_copilot.agent.support_orchestrator import root_agent

# optional: ensure env URLs for A2A are set
os.environ.setdefault("CATALOG_BASE_URL", "https://order-catalog-a2a-REPLACE.a.run.app")
os.environ.setdefault("COMPLIANCE_BASE_URL", "https://order-compliance-a2a-REPLACE.a.run.app")

runner = AgentRunner(root_agent)
app = FastAPI(title="Order Copilot Root Orchestrator")

class ChatIn(BaseModel):
    session_id: str
    text: str

@app.post("/chat")
async def chat(inp: ChatIn):
    # single-turn for simplicity; persist session externally in prod
    result = await runner.run_text(inp.text, user="user", session_id=inp.session_id)
    return {"response": result.response_text}
