# Parlant Integration Guide

## Overview

This project now integrates with **Parlant**, a framework for building structured, guideline-driven agents. This integration wraps the existing `mhc-agentic` tools and provides a new way to run the agent with explicit behavioral guidelines.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Parlant Agent

```bash
python parlant_integration/agent.py
```

This will start a local Parlant server and register the agent.

### 3. Interact with the Agent

Once the agent is running, you can interact with it via the Parlant UI:

1. Open your browser to `http://localhost:8800`
2. Select the **MHC-Agentic-Assistant** agent
3. Start chatting!

## Architecture

The integration wraps existing tools as Parlant tools:

- **`analyze_emotions`** → Wraps `EmotionTool`
- **`get_therapy_techniques`** → Wraps `TherapyTool`
- **`get_resources`** → Wraps `ResourceTool`
- **`assess_risk`** → Wraps `AssessmentTool`

### Guidelines

The agent operates under the following guidelines:

1. **Emotion Analysis**: Use `analyze_emotions` when the user expresses feelings.
2. **Therapy**: Use `get_therapy_techniques` when the user asks for help or coping strategies.
3. **Resources**: Use `get_resources` for information requests.
4. **Safety**: Use `assess_risk` when danger or distress is mentioned.

## Customization

To add more guidelines or tools, edit `parlant_integration/agent.py`:

```python
# Add a new guideline
await agent.create_guideline(
    condition="User asks about sleep",
    action="Provide sleep hygiene tips",
    tools=[get_resources]
)
```

## Comparison

| Feature | Original Agent (`run_agent.py`) | Parlant Agent (`parlant_integration/agent.py`) |
|---------|---------------------------------|------------------------------------------------|
| **Control** | LLM Controller (Prompt-based) | Parlant Guidelines (Structured) |
| **Tools** | Custom Tool Registry | Parlant Tool Wrappers |
| **Safety** | Fixed Pipeline (Stage 1) | Guideline-based + Tool-based |
| **UI** | CLI / Streamlit | Parlant Web UI |

## Troubleshooting

- **Port in use**: If port 8800 is busy, Parlant might fail to start.
- **Missing API Keys**: Ensure `.env` is loaded and keys are set (Groq/Gemini).
- **Import Errors**: Ensure you run the script from the root directory (`python parlant_integration/agent.py`).
