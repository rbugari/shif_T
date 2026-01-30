# Shift-T (Release R1.2) - Modernization Platform

Shift-T is an AI-powered agentic platform designed to automate the migration of legacy data technologies (SSIS, SQL Server, Oracle, MySQL) to modern PySpark/Databricks architectures using an **Execution Mesh** and **Knowledge Driver** system.

## 🚀 Quick Start

To start the entire platform (Backend + Frontend), simply run:

```bash
python run.py
```

This script will start the FastAPI backend (Port 8000) and the Next.js frontend (Port 3001).

## ✨ New in R1.2 (Premium Experience)

-   **Multi-Technology Core:** Automatic detection and handling of dialects (T-SQL, PL/SQL, MySQL) via the new **Knowledge Driver** system.
-   **Monaco Editor Integration:** Professional syntax highlighting for Python, SQL, and JSON across all views.
-   **Integrated Markdown Preview:** Seamlessly toggle between rendered documentation and raw code source.
-   **Fullscreen Mode:** Immersive work environment for auditing prompts and complex architecture graphs.
-   **Intelligence Hub:** Real-time visibility into AI compiled prompts and system knowledge injection.
-   **6-Stage Lifecycle:** Enhanced end-to-end workflow from Discovery to Solution Export.

## ✨ Key Features

-   **Interactive Execution Mesh:** Dynamic graph visualization using React Flow.
-   **Smart Triage:** Intelligent classification (CORE, SUPPORT, IGNORED) and gap analysis.
-   **Medallion Auto-Optimizer:** Automated refactoring to Bronze, Silver, and Gold architectural layers.
-   **Column-Level Lineage:** Automatic traceability from source field to target column.
-   **Professional PDF Reporting:** Generative summaries for executives and technical leads.

## 🛠️ Components
-   **Frontend**: Next.js 14, React Flow, Monaco Editor, Tailwind CSS.
-   **Backend**: FastAPI, LangGraph (Agent Orchestration), SqlGlot.
-   **Agents**:
    -   **Agent A (Librarian)**: Discovery & Triage.
    -   **Agent B (Cartographer)**: Topology & Mesh.
    -   **Agent C (Interpreter)**: Code Transpilation.
    -   **Agent F (Critic)**: Refinement & Medallion.
    -   **Agent G (Auditor)**: Governance & Compliance.

## 📖 Documentation
Explore our comprehensive [Documentation Center](docs/README.md):
-   [**Knowledge Drivers Architecture**](docs/knowledge_drivers.md)
-   [**The 6-Stage Migration Lifecycle**](docs/README.md#🚀-ciclo-de-vida-6-stages)
-   [Technical Specification](docs/SPECIFICATION.md)

---
*Shift-T: Automating de-complexification.*
