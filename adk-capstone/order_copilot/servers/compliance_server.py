import os
from dotenv import load_dotenv
from google.genai import types
from google.adk.models.google_llm import Gemini
from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY not set for compliance_server")

retry = types.HttpRetryOptions(attempts=5, exp_base=7, initial_delay=1,
                               http_status_codes=[429, 500, 503, 504])

def check_country_vat(country: str, vat_id: str) -> str:
    if country.lower() == "belgium" and len(vat_id.strip()) >= 8:
        return "COMPLIANT: VAT format OK."
    return "NON_COMPLIANT: Please verify VAT format & issuer."

agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite", api_key=API_KEY, retry_options=retry),
    name="compliance_agent",
    description="Vendor compliance checks (toy VAT check).",
    instruction="Call check_country_vat when asked about compliance.",
    tools=[check_country_vat],
)

app = to_a2a(agent, port=8002)
