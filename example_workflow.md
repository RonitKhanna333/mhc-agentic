Example Workflow

1) User asks a question.
2) The `Agent` constructs a prompt including recent memory.
3) The selected LLM (Groq or Gemini) generates a response.
4) Agent saves the exchange to memory and returns the response.

Extending the workflow
- Add tools (search, calculator, file-reading) and a tool-invocation pattern.
- Add a simple planner step: LLM proposes sub-steps; agent executes tools and confirms.
- Add safety checks, rate limits, and retries for robustness.
