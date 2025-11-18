Order Copilot — Multi-Agent Support Orchestrator (ADK + A2A + MCP)

A production-style, Enterprise Agents capstone showing how a Gemini-powered root orchestrator delegates to remote sub-agents over A2A, calls custom tools (including a long-running pause/resume flow), and bridges to MCP (Model Context Protocol) for external access. It ships with a Dev UI, traces/events, a small evaluation set, and Docker/Cloud Run paths.

Track: Enterprise Agents

Why: Customer support needs one assistant for product, compliance, shipping ETAs, and async risk scans

How: ADK root agent ⇄ A2A sub-agents + local tools + MCP bridge

Value: Clear routing, modular ownership, least-privilege boundaries, and cloud-ready deployment

🚀 Problem → Solution → Value

Problem
Support teams answer a mix of questions: product (stock/price), compliance (e.g., VAT), shipping ETAs, and long-running risk scans.

Solution
A root LLM agent (support_orchestrator) routes to the right capability:

Product → product_catalog_agent (A2A)

Compliance → compliance_agent (A2A)

Shipping ETA → shipping_eta (custom tool)

Risk Scan → start_risk_scan / resume_risk_scan (long-running)

Local note (demo) → mcp_fetch_file_note (MCP bridge stub)

Value
Independent evolvability (version, scale, governance) per capability, with observability & evaluation hooks.

🧱 Repository Layout
adk-capstone/
├─ README.md
├─ requirements.txt
├─ .env.example                 # safe template (no secrets)
├─ Dockerfile.root              # root agent image
├─ Dockerfile.catalog           # product catalog A2A service
├─ Dockerfile.compliance        # compliance A2A service
├─ order_copilot/
│  ├─ root_agent.yaml           # tells Dev UI which root agent to run
│  ├─ agent/
│  │  ├─ support_orchestrator.py
│  │  └─ __init__.py
│  ├─ servers/
│  │  ├─ product_catalog_server.py   # A2A @ :8001
│  │  ├─ compliance_server.py        # A2A @ :8002
│  │  └─ __init__.py
│  ├─ tools/                   # (optional stubs: ETA, long-run, MCP)
│  ├─ eval/
│  │  ├─ evalset.yaml
│  │  └─ cases.jsonl
│  └─ __init__.py
└─ scripts/
   ├─ run_catalog.ps1  / run_catalog.sh
   ├─ run_compliance.ps1 / run_compliance.sh
   └─ run_devui.ps1 / run_devui.sh

🧩 Architecture & Interactions
+------------------------------+    A2A (HTTP / Agent Card)    +---------------------------+
| Root LLM Agent               | ───────────────────────────▶   | product_catalog_agent     |
| support_orchestrator         |                               |  - get_product_info()     |
| (Gemini 2.5 Flash Lite)      | ◀───────────────────────────   |  - Agent Card @ :8001     |
|                              |                               +---------------------------+
| Tools: shipping_eta()        |
|        start_risk_scan()     |    A2A (HTTP / Agent Card)    +---------------------------+
|        resume_risk_scan()    | ───────────────────────────▶   | compliance_agent          |
|        mcp_fetch_file_note() |                               |  - check_country_vat()    |
|                              | ◀───────────────────────────   |  - Agent Card @ :8002     |
| Dev UI: traces/events/graph  |                               +---------------------------+
| MCP bridge (demo stub)  ─────────▶ filesystem / future MCP providers (Jira, Drive, DB)
+------------------------------+


Highlights

AUTO tool-calling lets Gemini pick the right tool/agent, then the root summarizes results into friendly answers.

A2A isolates sub-agents into separate services (own lifecycle & scale).

Long-running scans return a token; later, resume <token> completes.

MCP demo shows how to reach local/external systems safely via a protocol boundary.

✅ Feature Checklist (Course Rubric)

Multi-Agent System: Root LLM + two remote A2A sub-agents

Tools: custom (ETA, long-running) + MCP bridge stub

Long-running ops: start_risk_scan / resume_risk_scan with tokens

Sessions & State: Dev UI sessions + in-memory token cache

Observability: Dev UI Events/Graph/Trace across tools & A2A calls

Evaluation: order_copilot/eval/{evalset.yaml,cases.jsonl}

A2A Protocol: sub-agents exposed & consumed via Agent Cards

Deployment: Docker build/run; optional Cloud Run section below

📦 Getting Started

Repo: https://github.com/sanikacentric/KAGGLE--ADK-CAPSTONE--A2A-MCP-Multiagent/tree/main

1) Clone & Environment
git clone https://github.com/sanikacentric/KAGGLE--ADK-CAPSTONE--A2A-MCP-Multiagent.git
cd KAGGLE--ADK-CAPSTONE--A2A-MCP-Multiagent/adk-capstone


Create a virtual environment and install deps:

macOS/Linux

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


Windows (PowerShell)

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt


Copy the env template and set your key:

cp .env.example .env
# edit .env to set:
# GOOGLE_API_KEY=<your AI Studio key>
# CATALOG_BASE_URL=http://127.0.0.1:8001
# COMPLIANCE_BASE_URL=http://127.0.0.1:8002

2) Run A2A Sub-Agents (two terminals)

Product Catalog @ 8001

# macOS/Linux
source .venv/bin/activate
export GOOGLE_API_KEY="<YOUR_KEY>"
python -m uvicorn "order_copilot.servers.product_catalog_server:app" --host 127.0.0.1 --port 8001 --app-dir .

# Windows
.\.venv\Scripts\Activate.ps1
$env:GOOGLE_API_KEY = "<YOUR_KEY>"
python -m uvicorn "order_copilot.servers.product_catalog_server:app" --host 127.0.0.1 --port 8001 --app-dir .


Compliance @ 8002

# macOS/Linux
source .venv/bin/activate
export GOOGLE_API_KEY="<YOUR_KEY>"
python -m uvicorn "order_copilot.servers.compliance_server:app" --host 127.0.0.1 --port 8002 --app-dir .

# Windows
.\.venv\Scripts\Activate.ps1
$env:GOOGLE_API_KEY = "<YOUR_KEY>"
python -m uvicorn "order_copilot.servers.compliance_server:app" --host 127.0.0.1 --port 8002 --app-dir .


Health-check Agent Cards

curl -sI http://127.0.0.1:8001/.well-known/agent-card.json | head -n1
curl -sI http://127.0.0.1:8002/.well-known/agent-card.json | head -n1
# Expect HTTP/1.1 200 OK

3) Run ADK Dev UI (third terminal)
# macOS/Linux
source .venv/bin/activate
export GOOGLE_API_KEY="<YOUR_KEY>"
export CATALOG_BASE_URL="http://127.0.0.1:8001"
export COMPLIANCE_BASE_URL="http://127.0.0.1:8002"
adk web .

# Windows
.\.venv\Scripts\Activate.ps1
$env:GOOGLE_API_KEY      = "<YOUR_KEY>"
$env:CATALOG_BASE_URL    = "http://127.0.0.1:8001"
$env:COMPLIANCE_BASE_URL = "http://127.0.0.1:8002"
adk web .


Open http://127.0.0.1:8000 and chat.

4) Demo Prompts

Product (A2A)

“Is the iPhone 15 Pro in stock?”

“Price/specs for iPhone 15 Pro?”

“Do you have the Dell XPS 15 in stock?”

“What’s the price of Sony WH-1000XM5?”

Compliance (A2A)

“Check VAT for Belgium: BE01234567”

“Is VAT BE01234567 valid for Belgium?”

Shipping ETA (tool)

“What’s the shipping ETA to 07001?”

“Estimate delivery to 90210.”

Long-running (tools)

“scan order ORD-42” → returns a token

“resume <token>” or “resume last”

MCP (demo stub)

“fetch note ./notes/todo.txt”

🔎 Observability

Use Dev UI → Events / Graph / Trace to see each tool call, A2A hop, and final LLM summary. Logs show session IDs and server health as you interact.

🧪 Evaluation

Small smoke-test eval lives in order_copilot/eval.

Files

cases.jsonl — prompt + expected text snippets

evalset.yaml — ADK eval definition

Run

adk eval order_copilot/eval/evalset.yaml

🐳 Docker (local images)

Build images from the repo root:

# Root agent (Dev UI runner)
docker build -f Dockerfile.root -t ordercopilot/root:local .

# A2A sub-agents
docker build -f Dockerfile.catalog -t ordercopilot/catalog:local .
docker build -f Dockerfile.compliance -t ordercopilot/compliance:local .


Run containers:

# product catalog @ 8001
docker run --rm -p 8001:8001 \
  -e GOOGLE_API_KEY=$GOOGLE_API_KEY \
  ordercopilot/catalog:local

# compliance @ 8002
docker run --rm -p 8002:8002 \
  -e GOOGLE_API_KEY=$GOOGLE_API_KEY \
  ordercopilot/compliance:local

# Dev UI / root agent @ 8000
docker run --rm -p 8000:8000 \
  -e GOOGLE_API_KEY=$GOOGLE_API_KEY \
  -e CATALOG_BASE_URL=http://host.docker.internal:8001 \
  -e COMPLIANCE_BASE_URL=http://host.docker.internal:8002 \
  ordercopilot/root:local


On Linux, replace host.docker.internal with your host IP (e.g., 172.17.0.1) or run all three in a shared Docker network.

☁️ (Optional) Deploy to Cloud Run

Tag & Push images (example uses gcr.io/PROJECT/…):

PROJECT_ID=<your-gcp-project>
gcloud auth configure-docker

docker tag ordercopilot/catalog:local gcr.io/$PROJECT_ID/ordercopilot-catalog:v1
docker tag ordercopilot/compliance:local gcr.io/$PROJECT_ID/ordercopilot-compliance:v1
docker tag ordercopilot/root:local     gcr.io/$PROJECT_ID/ordercopilot-root:v1

docker push gcr.io/$PROJECT_ID/ordercopilot-catalog:v1
docker push gcr.io/$PROJECT_ID/ordercopilot-compliance:v1
docker push gcr.io/$PROJECT_ID/ordercopilot-root:v1


Deploy A2A services (public for demo; lock down in prod):

gcloud run deploy ordercopilot-catalog \
  --image gcr.io/$PROJECT_ID/ordercopilot-catalog:v1 \
  --platform managed --region us-central1 --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=<YOUR_KEY>

gcloud run deploy ordercopilot-compliance \
  --image gcr.io/$PROJECT_ID/ordercopilot-compliance:v1 \
  --platform managed --region us-central1 --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=<YOUR_KEY>


Deploy root / Dev UI

gcloud run deploy ordercopilot-root \
  --image gcr.io/$PROJECT_ID/ordercopilot-root:v1 \
  --platform managed --region us-central1 --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=<YOUR_KEY>,\
CATALOG_BASE_URL=<CATALOG_CLOUDRUN_URL>,\
COMPLIANCE_BASE_URL=<COMPLIANCE_CLOUDRUN_URL>


Open the root service URL and chat.

Prod notes: Use VPC-E, private egress, workload identity, and restrict public access; set per-service IAM; store secrets in Secret Manager; pin ADK versions.

🧠 Why ADK, A2A, and MCP matter

ADK (Agent Development Kit): Standard way to compose LLMs, tools, memory, and remote agents with observability and evaluation. Opinionated enough for enterprise guardrails yet flexible for innovation.

A2A (Agent-to-Agent): Defines how agents discover and call each other via Agent Cards and clean HTTP contracts. Teams can own sub-agents independently, scale them separately, and enforce least-privilege.

MCP (Model Context Protocol): Adds a secure boundary to reach local/enterprise resources (filesystems, Jira, Git, DBs) through providers, avoiding direct arbitrary system access from the LLM.

🧯 Troubleshooting

FunctionTool kwargs (name/description)
This repo’s support_orchestrator.py uses docstrings so it works with older ADK where FunctionTool accepts only the callable. If you upgrade ADK and want explicit names/descriptions, you can re-enable the keyword args.

Agent Cards 404
Ensure the two A2A servers are running and reachable. Check CATALOG_BASE_URL and COMPLIANCE_BASE_URL.

CORS / Cloud Run
If the root service calls sub-agents across domains, configure allowed origins and service-to-service auth or make them private with VPC/E and authorized invocations.
