# Technical Specification: Gartner Loan Supervisor Multi-Agent Ecosystem (v20260508.5)

This specification documents the architectural design, sub-agent roles, tools, execution flows, and response databases of the modular **Loan Supervisor Agent (v20260508.5)** deployed on Vertex AI Reasoning Engine.

---

## 1. System Architecture & Folder Layout

The system is designed as a hierarchical, multi-agent orchestrator using the **Google Cloud ADK (Agent Development Kit)** framework. 

The orchestrator delegates core underwriting tasks to a unified `SequentialAgent` (`loan_processing_sequence`) which coordinates the five specialist sub-agents sequentially.

```
loan_supervisor/
├── Makefile
├── pyproject.toml
├── README.md
├── spec.md
└── app/
    ├── agent.py                 <-- Master Orchestrator Agent (Flow router)
    ├── prompt.md                <-- Orchestrator Instructions (3 distinct flows)
    ├── responses.toml           <-- Central Responses & Underwriting Database (L_0001 to L_0010)
    ├── shared/
    │   ├── __init__.py
    │   ├── callbacks.py         <-- Shared Telemetry & Callback hooks
    │   └── model.py             <-- Shared Model (Gemini 2.5 Flash) & GCP Client Setup
    └── agents/
        ├── document_retriever/
        │   ├── agent.py         <-- Document Retriever Sub-Agent (Calls fetch_application_files)
        │   └── prompt.md
        ├── document_validator/
        │   ├── agent.py         <-- Document Validator Sub-Agent (Calls extract_and_validate_document_fields)
        │   └── prompt.md
        ├── credit_checker/
        │   ├── agent.py         <-- Credit Checker Sub-Agent (Calls retrieve_bureau_credit_profile)
        │   └── prompt.md
        ├── risk_assessor/
        │   ├── agent.py         <-- Risk Assessor Sub-Agent (Calls evaluate_underwriting_risk_score)
        │   └── prompt.md
        └── summarization_agent/
            ├── agent.py         <-- Summarization Agent (Calls summarize_response)
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
    
    DocsRetriever -->|Tool| RetrieverTool[fetch_application_files]
    DocsValidator -->|Tool| ValidatorTool[extract_and_validate_document_fields]
    CreditChecker -->|Tool| CreditTool[retrieve_bureau_credit_profile]
    RiskAssessor -->|Tool| RiskTool[evaluate_underwriting_risk_score]
    SummarizationAgent -->|Tool| SummarizationTool[summarize_response]
    
    RetrieverTool -->|Reads| DB[(app/responses.toml)]
    ValidatorTool -->|Reads| DB
    CreditTool -->|Reads| DB
    RiskTool -->|Reads| DB
    SummarizationTool -->|Reads| DB
```

---

## 2. Central Responses Database (`responses.toml`)

To ensure a deterministic, high-fidelity, and consistent experience during demonstrations, all sub-agents and the final summarizer query the **unified database** located at:
👉 **`loan_supervisor/app/responses.toml`**

### 💡 Crucial Guidance for AI Agents and Humans:
* **Where to Tweak Responses**: If you want to change, enhance, or mock different results (such as modifying a FICO score, adding new warning flags, or renaming files) for any loan ID from `L_0001` to `L_0010`, **do not edit the python agent scripts or prompts.** Instead, modify the corresponding block under the appropriate table header in `responses.toml`.
* **Available Tables**:
  1. `[responses]`: Houses the final Markdown-formatted decision summary table returned to the user by `Summarization_Agent`.
  2. `[document_retriever]`: Houses simulated OCR document retrieval metadata returned by `Document_Retriever`.
  3. `[document_validator]`: Houses simulated field validation verification metrics returned by `Document_Validator`.
  4. `[credit_checker]`: Houses simulated Credit Bureau FICO profile assessments returned by `Credit_Checker`.
  5. `[risk_assessor]`: Houses simulated calculated Underwriting Risk evaluations returned by `Risk_Assessor`.

---

## 3. Supported Flows & Component Schema

### A. Flow 1: Process a Loan Application
When asked to process a loan:
1. Orchestrator delegates processing to the `loan_processing_sequence` subagent.
2. `loan_processing_sequence` coordinates the five modular subagents sequentially:
   - **`Document_Retriever`**: Normalizes the application ID and executes the `fetch_application_files` tool to pull details from `responses.toml` `[document_retriever]`.
   - **`Document_Validator`**: Extracts the ID and executes the `extract_and_validate_document_fields` tool to pull validation checks from `responses.toml` `[document_validator]`.
   - **`Credit_Checker`**: Extracts the ID and executes the `retrieve_bureau_credit_profile` tool to fetch credit details from `responses.toml` `[credit_checker]`.
   - **`Risk_Assessor`**: Extracts the ID and executes the `evaluate_underwriting_risk_score` tool to calculate risk categories from `responses.toml` `[risk_assessor]`.
   - **`Summarization_Agent`**: Extracts the ID and executes the `summarize_response` tool to pull the final decision table from `responses.toml` `[responses]`.
3. Orchestrator receives the verbatim table from the sequence and outputs it verbatim to the user, keeping the intermediate sub-agent traces hidden from the final response text.

### B. Flow 2: Get Unprocessed Mortgage Loan Applications
* **Trigger**: "Give the latest X unprocessed mortgage loan applications."
* **Tool called**: `get_unprocessed_applications(limit)`
* **Details**: Reads `/Users/gvarelal/Documents/demos/gartner/pending_applications.md` to find pending intake files.

### C. Flow 3: Summarize Batch Processing Operations
* **Trigger**: "Summarize the loan applications processed in the last batch."
* **Tool called**: `summarize_batch_processing()`
* **Details**: Reads the comprehensive operations report `/Users/gvarelal/Documents/demos/gartner/loan_processing_report.md`.

---

## 4. Toolchain & Commands

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
