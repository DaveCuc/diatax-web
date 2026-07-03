<p align="center">
  <h1 align="center">Diátaxis Web</h1>
   <h2 align="center">Automated Technical Documentation Generator</h2>
</p>

<p align="center"> 
   <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white" alt="Python 3.10+"/> 
   <img src="https://img.shields.io/badge/Framework-Google%20ADK%202.0-4285F4?logo=google&logoColor=white" alt="Google ADK 2.0"/> 
   <img src="https://img.shields.io/badge/Workflow-Graph%20Workflow%20API-purple" alt="Graph Workflow API"/> 
   <img src="https://img.shields.io/badge/Architecture-Multi--Agent-8A2BE2" alt="Multi-Agent"/> 
   <img src="https://img.shields.io/badge/Framework-Diátaxis-2ea44f" alt="Diátaxis Framework"/> 
   <img src="https://img.shields.io/badge/Execution-Local%20Sandbox-orange" alt="Local Sandbox"/> 
</p>


Diátaxis Web is an automated technical documentation generation system powered by **Google Agent Development Kit (ADK) 2.0** utilizing the new **Graph Workflow API**. It processes public GitHub repositories, analyzes the code architecture, and writes documentation aligned to the four pillars of the Diátaxis framework (Tutorials, How-To Guides, References, and Explanations) inside an isolated local sandbox.

---

## Key Features

- **ADK 2.0 Graph Workflow API**: Structured using a function-based graph layout (Orchestrator and Researcher nodes) rather than legacy sequential structures.
- **Isolated Workspace Sandbox**: Clones public GitHub repositories into distinct session directories (`workspace_tmp/[UUID]`) and sanitizes dependencies, lock files, binary files, and metadata (simulating Google Sandboxes) before analysis.
- **Writers & Judges Validation Loop**: Executes a deterministic quality review loop (maximum 3 iterations) where specialized Judges evaluate drafted content against Diátaxis guidelines.
- **A2UI SiteWriter Integration**: Renders clean HTML/CSS/JS static documentation sites based on the custom specifications defined in `sitewriter.md`, compiled into a download-ready `.zip`.
- **Security Guardrails**: The analysis pipeline excludes hidden internal tool directories such as `.agents/skills`, detects prompt-injection payloads in source files, and ignores suspicious files completely.
- **Background Cleanup**: Automatically purges session workspace directories once a document dispatch is completed.

---

## Installation & Setup

### 1. Prerequisites
- Python 3.11 or later
- [uv](https://docs.astral.sh/uv/getting-started/installation/index.md) (highly recommended fast package installer)

### 2. Environment Configuration
Clone the environment template and configure your parameters:
```bash
cp .env.example .env
```

To configure your API credentials (either Google AI Studio API Key or Google Cloud SDK/Vertex AI), refer to the detailed [AUTH_SETUP.md](AUTH_SETUP.md) guide.

### 3. Install Dependencies
Create the environment and install package dependencies:
```bash
uv venv
uv pip install -r pyproject.toml
```

---

## Running the Application

### Start the Development Server
To launch the FastAPI backend server (which serves the frontend landing page at `http://localhost:8000/` and provides the orchestration endpoints):
```bash
uv run python app/fast_api_app.py
```

### Run Locally (Console Test)
To execute a test run of the graph workflow locally using a sample repository payload:
```bash
uv run python main.py
```


