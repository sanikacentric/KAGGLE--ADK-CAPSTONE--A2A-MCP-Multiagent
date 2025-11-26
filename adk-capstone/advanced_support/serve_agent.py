import os
import sys
import uvicorn
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from advanced_support.advanced_agent import advanced_agent

# Create the A2A app
app = to_a2a(advanced_agent, port=8005)

if __name__ == "__main__":
    print("Starting Advanced Support Agent on port 8005...")
    uvicorn.run(app, host="0.0.0.0", port=8005)
