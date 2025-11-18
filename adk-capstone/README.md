Order Copilot — Multi-Agent Support Orchestrator (ADK + A2A + MCP)

A production-style, Enterprise Agents capstone showing how an LLM-powered root orchestrator delegates to remote sub-agents over A2A, calls custom tools (including a long-running pause/resume flow), and bridges to MCP (Model Context Protocol) for external system access. It includes Dev UI, observability (traces/events), an evaluation set, and Docker/Cloud Run deployment paths.

🎯 Problem → Solution → Value

Problem: Customer support teams need a single assistant that can answer product questions (price/stock), check compliance (e.g., VAT), give shipping ETAs, and run risk scans that may take time to complete.

Solution: A root LLM agent (“support_orchestrator”) routes each user request to the right remote sub-agent or tool:

Product questions → product_catalog_agent (A2A)

Compliance questions → compliance_agent (A2A)

Shipping ETA → shipping_eta (custom tool)

Risk scan → start_risk_scan / resume_risk_scan (long-running)

Local file note (demo) → mcp_fetch_file_note (MCP bridge)

Value: Clear routing, modular ownership, and enterprise-ready connectivity: each capability can evolve independently, scale separately, and be governed by least-privilege boundaries.

🧱 Repo Layout
adk-capstone/
├─ README.md                     ← you are here
├─ requirements.txt
├─ .env                          ← GOOGLE_API_KEY, CATALOG/COMPLIANCE base URLs
├─ Dockerfile.root               ← root agent image
├─ Dockerfile.catalog            ← product catalog A2A service
├─ Dockerfile.compliance         ← compliance A2A service
├─ order_copilot/
│  ├─ root_agent.yaml            ← tells Dev UI which agent to run
│  ├─ agent/
│  │  ├─ support_orchestrator.py ← root LLM agent (Gemini)
│  │  ├─ __init__.py
│  ├─ servers/
│  │  ├─ product_catalog_server.py  ← exposes Agent Card on :8001
│  │  ├─ compliance_server.py       ← exposes Agent Card on :8002
│  │  ├─ __init__.py
│  ├─ tools/ (optional extras / stubs)
│  ├─ eval/
│  │  ├─ evalset.yaml
│  │  ├─ cases.jsonl
│  ├─ __init__.py
└─ scripts/
   ├─ run_catalog.ps1 / run_catalog.sh
   ├─ run_compliance.ps1 / run_compliance.sh
   └─ run_devui.ps1 / run_devui.sh

🧩 Architecture & Interactions
+-----------------------------+       A2A (JSON-RPC / HTTP)       +---------------------------+
|  Root LLM Agent             |  ───────────────────────────────▶  | product_catalog_agent     |
|  support_orchestrator       |                                    |  - get_product_info()     |
|  (Gemini 2.5 Flash Lite)    |  ◀───────────────────────────────  |  - Agent Card @ :8001     |
|  - routing (policy)         |                                    +---------------------------+
|  - tool calling             |
|  - summarization            |       A2A (JSON-RPC / HTTP)       +---------------------------+
|  Tools:                     |  ───────────────────────────────▶  | compliance_agent          |
|   • shipping_eta()          |                                    |  - check_country_vat()    |
|   • start_risk_scan()       |  ◀───────────────────────────────  |  - Agent Card @ :8002     |
|   • resume_risk_scan()      |                                    +---------------------------+
|   • mcp_fetch_file_note()   |
|                             |         MCP bridge (demo)
|  Dev UI: Traces & Events    |  ───────────────────────────────▶  filesystem / future tools
+-----------------------------+


Flow highlights

The root agent uses Gemini with AUTO tool-calling to pick the correct sub-agent/tool.

A2A keeps remote agents independent (separate processes, separate repos if needed).

Long-running: start_risk_scan() returns a token; later the user says resume <token> and the root calls resume_risk_scan().

MCP: mcp_fetch_file_note() shows how you’d bridge to MCP-speaking systems (today a filesystem demo; tomorrow: Jira, Drive, Git, DBs, etc.).

Observability: Use Dev UI’s Events/Graph/Trace to see every step across tools and A2A calls.

✅ Feature Checklist (Course Rubric)

Multi-Agent System: Root LLM agent + two remote A2A sub-agents (product & compliance).

Tools:

Custom tools: shipping_eta, start_risk_scan, resume_risk_scan

MCP bridge: mcp_fetch_file_note (filesystem demo stub; replace with real MCP tool later)

Long-running ops: pause/resume via token.

Sessions & State: ADK Dev UI sessions; in-memory token cache for scans.

Observability: Dev UI events, graph, and debug traces.

Agent Evaluation: order_copilot/eval/{evalset.yaml,cases.jsonl}.

A2A Protocol: both sub-agents exposed and consumed via A2A Agent Cards.

🔧 Prerequisites

Python (3.10+ recommended)

A Google API key in .env:

GOOGLE_API_KEY=your_key_here


Optional overrides:

CATALOG_BASE_URL=http://127.0.0.1:8001
COMPLIANCE_BASE_URL=http://127.0.0.1:8002


Install Python deps:

python -m venv .venv
source .venv/bin/activate   # (PowerShell) .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Free all ports


foreach ($p in 8000,18000,8001,8002) {
  Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique |
    ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
}

Activate  .\.venv\Scripts\Activate.ps1

# Terminal A (8001)
$env:GOOGLE_API_KEY = "<NEW_AISTUDIO_KEY>"
python -m uvicorn "order_copilot.servers.product_catalog_server:app" --host 127.0.0.1 --port 8001 --app-dir .

# Terminal B (8002)
$env:GOOGLE_API_KEY = "<NEW_AISTUDIO_KEY>"
python -m uvicorn "order_copilot.servers.compliance_server:app" --host 127.0.0.1 --port 8002 --app-dir .

# Terminal C (Dev UI)
$env:GOOGLE_API_KEY      = "<NEW_AISTUDIO_KEY>"
$env:CATALOG_BASE_URL    = "http://127.0.0.1:8001"
$env:COMPLIANCE_BASE_URL = "http://127.0.0.1:8002"
adk web .



Invoke-WebRequest http://127.0.0.1:8001/.well-known/agent-card.json -UseBasicParsing | Select StatusCode
Invoke-WebRequest http://127.0.0.1:8002/.well-known/agent-card.json -UseBasicParsing | Select StatusCode
# expect 200 for both


Use the exact product names your catalog server knows:
•	“Is the iPhone 15 Pro in stock?”
•	“Price/specs for iPhone 15 Pro?”
•	“Do you have the Dell XPS 15 in stock?”
•	“What’s the price of Sony WH-1000XM5?”
(If you want it to handle typos like “iphone pro 15”, add a fuzzy-match as I showed earlier.)
3) Compliance (remote A2A) – good questions
Your compliance server exposes check_country_vat:
•	“Check VAT for Belgium: BE01234567”
•	“Is VAT BE01234567 valid for Belgium?”
•	“Compliance check: country=Belgium, vat=BE01234567”
4) Shipping ETA (local tool)
•	“What’s the shipping ETA to 08901?” (0–3* ZIP prefix → ~2 business days)
•	“Estimate delivery to 90210” (other prefixes → ~5 business days)
5) MCP file note (demo stub)
•	“fetch note ./notes/todo.txt”
The root agent will call mcp_fetch_file_note and echo the file path (demo behavior).
