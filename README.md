# ResolveAI: Autonomous Ticket Resolution Agent

ResolveAI is a production-grade Generative AI project that acts as an autonomous ticket resolution agent. It uses prompt engineering, MCP (Model Context Protocol), agentic AI, FastAPI, Docker, and CI/CD on the cloud.

## Overview

Support and operations teams receive a high volume of repetitive, well-structured tickets. ResolveAI reads incoming tickets, identifies the intent, plans a resolution, calls backend systems (simulated here) to gather facts and take action, resolves the ticket when confident, and escalates to a human with a full diagnosis when it is not.

## Features

- **FastAPI Front Door**: Receives tickets over HTTP and exposes health checks.
- **LangGraph AI Agent**: The "brain" that classifies intent, plans steps, evaluates tool results, and decides to act or escalate.
- **MCP Servers (Mocked)**: Standardized interfaces for tools like order lookup, refunds, and password resets.
- **Safe & Policy-Driven**: No irreversible action is taken without passing an explicit confidence and policy check.

## Setup & Running

1. **Prerequisites**: Ensure you have Python 3.11+, Docker, and Docker Compose installed.
2. **Environment**: You must set a valid OpenAI API key.
   ```bash
   export OPENAI_API_KEY="your_api_key_here"
   ```

### Using Docker (Recommended)
```bash
docker-compose up --build
```
The API will be available at `http://localhost:8000`.

### Local Development
```bash
pip install -r requirements.txt
export PYTHONPATH=$(pwd)
uvicorn src.api.main:app --reload
```

## Testing the System

You can test the system using the provided `demo_script.py`:
```bash
python demo_script.py
```

## Project Structure
- `src/api/`: FastAPI application code.
- `src/agent/`: LangGraph agent, state, and prompts.
- `src/mcp_servers/`: Mocked MCP servers for tools.
- `.github/workflows/`: CI/CD pipelines.

## Documentation
- [ARCHITECTURE.md](ARCHITECTURE.md): System architecture and workflow diagrams.
- [EVALUATION_REPORT.md](EVALUATION_REPORT.md): Example AI evaluation metrics.
