# Synapse-Dx

A Neuro-Symbolic KG-RAG Diagnostic Engine. Achieves <500ms retrieval latency by fusing vector search (Qdrant) with structured medical ontologies (Neo4j/PrimeKG) to ground LLM reasoning in verified clinical protocols.

## Setup Instructions

### 1. Infrastructure (Neo4j & Qdrant)
We use Docker to run the database services.
```bash
docker compose up -d
```
This starts:
- **Neo4j** (Graph DB) on ports 7474 (UI) and 7687 (Bolt).
- **Qdrant** (Vector DB) on port 6333.
- **PostgreSQL** (Memory DB) on port 5532.

### 2. Python Environment
Install the required dependencies:
```bash
pip install -r requirements.txt
```

### 2.1. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 3. Configuration
Copy `.env.example` to `.env` and add your API keys:
```bash
cp .env.example .env
```
- Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/).

## Key Features
- **"Dr. House" Persona**: The agent acts as a consultative doctor, asking clarifying questions before diagnosing.
- **Conversational Memory**: Remembers user details and context across sessions (powered by PostgreSQL).
- **Hybrid RAG**: Combines Vector Search (Qdrant) and Knowledge Graph (Neo4j) for accurate medical retrieval.
- **Real-time Triage**: Streaming responses with <50ms latency.

## Project Structure
- `src/`: Backend source code (FastAPI, Agno Agent).
- `frontend/`: Next.js Chat Interface.
- `scripts/`: Data loading scripts.
- `Docs/`: Medical textbooks and guidelines.