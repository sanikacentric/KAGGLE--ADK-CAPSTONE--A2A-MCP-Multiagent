import os
from dotenv import load_dotenv
from google.genai import types
from google.adk.models.google_llm import Gemini
from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

load_dotenv()  # lets it read GOOGLE_API_KEY from .env too
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY not set for product_catalog_server")

retry = types.HttpRetryOptions(attempts=5, exp_base=7, initial_delay=1,
                               http_status_codes=[429, 500, 503, 504])

CATALOG = {
    "iphone 15 pro": "iPhone 15 Pro, $999, Low Stock (8), 128GB, Titanium",
    "dell xps 15":   'Dell XPS 15, $1,299, In Stock (45), 15.6", 16GB, 512GB SSD',
    "sony wh-1000xm5":"Sony WH-1000XM5, $399, In Stock (67), ANC, 30h battery",
}

def get_product_info(product_name: str) -> str:
    p = product_name.lower().strip()
    return f"Product: {CATALOG[p]}" if p in CATALOG else "Not found"

agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite", api_key=API_KEY, retry_options=retry),
    name="product_catalog_agent",
    description="Vendor product catalog (price/stock/specs).",
    instruction="Use get_product_info to answer product questions. Be concise.",
    tools=[get_product_info],
)

app = to_a2a(agent, port=8001)
