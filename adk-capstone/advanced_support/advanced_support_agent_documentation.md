# Advanced Support Customer Agent - Comprehensive Guide

## 1. Overview
The **Advanced Support Customer Agent** is a strategic addition to the ADK Capstone project. It serves as a **Supervisor Agent** that wraps the existing `support_orchestrator` (Root Agent). Instead of replacing the existing logic, it adds a layer of governance, validation, and quality assurance.

## 2. Importance of Supervision
In autonomous agent systems, "trust but verify" is a critical design principle. The Advanced Support Agent provides:

*   **Quality Control**: It validates the output of the operational agent before it reaches the customer.
*   **Hallucination Prevention**: By cross-referencing the sub-agent's response with its own instructions, it can catch nonsensical or incorrect answers.
*   **Escalation Protocol**: It has a dedicated channel (`notify_customer_support`) to flag issues to human operators, ensuring that bad customer experiences are caught early.
*   **Separation of Concerns**: The operational agent focuses on *doing* (checking stock, shipping), while the supervisor focuses on *monitoring* (is this answer helpful? is it polite?).

## 3. Folder Architecture
The implementation is isolated in a dedicated directory to maintain a clean codebase.

```text
adk-capstone/
├── advanced_support/               # [NEW] Dedicated folder for the supervisor
│   ├── __init__.py                 # Makes it a Python package
│   ├── advanced_agent.py           # Core logic: The Supervisor Agent definition
│   ├── serve_agent.py              # Server script to expose the agent via HTTP/A2A
│   ├── test_agent.py               # Verification script to test the agent
│   └── advanced_support_agent_documentation.md # This documentation
├── order_copilot/                  # [EXISTING] The operational agent code
│   ├── agent/
│   │   └── root_agent.py           # The inner agent being supervised
│   └── ...
└── ...
```

## 4. Technical Implementation

### The Supervisor Agent (`advanced_agent.py`)
This file defines the `AdvancedSupportAgent`. It uses the **Gemini 3.0 Pro** model for high-reasoning capabilities.

**Key Features:**
*   **Model**: `gemini-3.0-pro-001` (Selected for superior reasoning and validation skills).
*   **Sub-Agent**: Imports `root_agent` from `order_copilot` and treats it as a tool/sub-agent.
*   **Tools**: `notify_customer_support` allows it to "raise a hand" when things go wrong.

### Workflow
1.  **Input**: User asks a question (e.g., "Where is my order?").
2.  **Delegation**: Supervisor calls the `support_orchestrator` sub-agent.
3.  **Execution**: `support_orchestrator` checks the database/tools and returns an answer.
4.  **Validation**: Supervisor reviews the answer.
    *   *Scenario A (Good)*: Answer is "Arriving Tuesday." -> Supervisor relays this to user.
    *   *Scenario B (Bad)*: Answer is "I don't know." or incorrect -> Supervisor calls `notify_customer_support("Agent failed to find order")` and apologizes to user.

## 5. Running the Agent

### As a Service
To run the agent as a standalone A2A service:
```bash
python advanced_support/serve_agent.py
```
*Runs on port 8005.*

### Verification
To test the agent's logic:
```bash
python advanced_support/test_agent.py
```
