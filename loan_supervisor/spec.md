# Technical Specification: Gartner Loan Supervisor Multi-Agent Ecosystem (v20260508.1)

This specification documents the architectural design, sub-agent roles, tools, and execution flows of the modular **Loan Supervisor Agent (v20260508.1)** deployed on Vertex AI Reasoning Engine.

---

## 1. System Architecture & Folder Layout

The system is designed as a hierarchical, multi-agent orchestrator using the **Google Cloud ADK (Agent Development Kit)** framework. 

The orchestrator delegates core underwriting tasks to a unified `SequentialAgent` (`loan_processing_sequence`) which coordinates the specialist sub-agents sequentially.

```
loan_supervisor/
├── Makefile
├── pyproject.toml
├── README.md
├── spec.md
└── app/
    ├── agent.py                 <-- Master Orchestrator Agent (Flow router)
    ├── prompt.md                <-- Orchestrator Instructions (3 distinct flows)
    ├── responses.toml           <-- Verbatim Responses Database (L_0001 to L_0010)
    ├── shared/
    │   ├── __init__.py
    │   ├── callbacks.py         <-- Shared Telemetry & Callback hooks
    │   └── model.py             <-- Shared Model (Gemini 2.5 Flash) & GCP Client Setup
    └── agents/
        ├── document_retriever/
        │   ├── agent.py         <-- Document Retriever Sub-Agent (Demo Mode)
        │   └── prompt.md
        ├── document_validator/
        │   ├── agent.py         <-- Document Validator Sub-Agent (Demo Mode)
        │   └── prompt.md
        ├── credit_checker/
        │   ├── agent.py         <-- Credit Checker Sub-Agent (Demo Mode)
        │   └── prompt.md
        ├── risk_assessor/
        │   ├── agent.py         <-- Risk Assessor Sub-Agent (Demo Mode)
        │   └── prompt.md
        └── summarization_agent/
            ├── agent.py         <-- Summarization Agent (Verbatim output retriever)
            └── prompt.md
```

```mermaid
graph TD
    Orchestrator[LoanSupervisorAgent] -->|SubAgent| Sequence[loan_processing_sequence (SequentialAgent)]
    Orchestrator -->|Tool| Unprocessed[get_unprocessed_applications]
    Orchestrator -->|Tool| Summary[summarize_batch_processing]
    
    Sequence -->|1| DocsRetriever[Document_Retriever]
    Sequence -->|2| DocsValidator[Document_Validator]
    Sequence -->|3| CreditChecker[Credit_Checker]
    Sequence -->|4| RiskAssessor[Risk_Assessor]
    Sequence -->|5| SummarizationAgent[Summarization_Agent]
    
    SummarizationAgent -->|Tool| DeterministicTool[summarize_response]
```

---

## 2. Supported Flows & Component Schema

### A. Flow 1: Process a Loan Application
When asked to process a loan:
1. Orchestrator delegates processing to the `loan_processing_sequence` subagent.
2. `loan_processing_sequence` coordinates the 5 modular subagents sequentially:
   - **`Document_Retriever`**: Normalizes the application ID and returns it (Demo Mode).
   - **`Document_Validator`**: Receives the ID and returns it (Demo Mode).
   - **`Credit_Checker`**: Receives the ID and returns it (Demo Mode).
   - **`Risk_Assessor`**: Receives the ID and returns it (Demo Mode).
   - **`Summarization_Agent`**: Deterministically queries `responses.toml` using the `summarize_response` tool, and returns the exact final underwriting table verbatim.
3. Orchestrator receives the verbatim table from the sequence and outputs it verbatim to the user.

### B. Flow 2: Get Unprocessed Mortgage Loan Applications
- **Trigger**: "Give the latest X unprocessed mortgage loan applications."
- **Tool called**: `get_unprocessed_applications(limit)`
- **Details**: Reads `/Users/gvarelal/Documents/demos/gartner/pending_applications.md` to find pending intake files.

### C. Flow 3: Summarize Batch Processing Operations
- **Trigger**: "Summarize the loan applications processed in the last batch."
- **Tool called**: `summarize_batch_processing()`
- **Details**: Reads the comprehensive operations report `/Users/gvarelal/Documents/demos/gartner/loan_processing_report.md`.

---

## 3. Toolchain & Commands

### Local Development

```bash
# Sync dependencies workspace-wide
make install

# Start the interactive local agent playground
make playground
```

### Deployment to Vertex AI Reasoning Engine

```bash
# Perform dry-run check
make deploy-dry-run PROJECT=demo4events10

# Deploy to target GCP project
make deploy PROJECT=demo4events10
```
