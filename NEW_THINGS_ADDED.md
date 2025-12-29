# New Things Added

This document summarizes notable files/folders that were recently added to this repo.

## Docs

- `QUICKSTART.md`
  - End-to-end setup and usage guide, including tracing and prompt optimization workflows.

## Demo

- `demo.py`
  - A runnable demo script for exercising the agent system.

## Agent-Lightning Outputs

- `learned_policy/learned_policy.json`
  - A learned policy artifact produced by training/optimization.

- `optimized_prompts/`
  - `all_variants.json`: all candidate prompt variants explored.
  - `best_prompt.txt`: the selected/best prompt.
  - `optimization_summary.json`: summary of the optimization run.

## Parlant Caches / Logs

- `parlant-data/`
- `parlant_integration/parlant-data/`

These contain cache JSONs and logs (e.g., embeddings cache, evaluation cache, `parlant.log`). Depending on your workflow, you may prefer to treat these as generated artifacts and exclude them via `.gitignore`.
