# Agent-Lightning Integration Guide

## Overview

This chatbot now includes **Agent-Lightning** integration for trace collection, prompt optimization (APO), and reinforcement learning (RL) training.

## Quick Start

### 1. Enable Tracing

Set the environment variable to collect traces:

```bash
# In .env file
ENABLE_TRACING=true
```

### 2. Run the Agent

```bash
python run_agent.py
```

Traces will be saved to `traces/YYYYMMDD/` as JSON files.

### 3. Analyze Traces

```bash
python scripts/train_agent.py --mode=analyze
```

This shows statistics about collected traces and computes reward scores.

### 4. Run Optimization

```bash
python scripts/train_agent.py --mode=apo --output-dir=optimized_prompts
```

This analyzes traces and identifies best-performing prompts.

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Enable/disable tracing (default: false)
ENABLE_TRACING=true

# LLM settings (existing)
LLM_PROVIDER=groq
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.1-8b-instant
GROQ_MASTER_MODEL=llama-3.3-70b-versatile

# Debug mode
DEBUG_MODE=false
```

## Architecture

### Instrumentation Flow

```
User Input → LLM Client → TracedLLMClient → TraceStore
                ↓
            Response
                ↓
         Saved to traces/
```

### Components

1. **TracedLLMClient** (`instrumentation/agent_tracing.py`)
   - Wraps all LLM calls
   - Records inputs, outputs, latency
   - Controlled by `ENABLE_TRACING` env var

2. **TraceStore** (`instrumentation/trace_store.py`)
   - Saves traces to disk as JSON
   - Organizes by date: `traces/YYYYMMDD/*.json`
   - Provides query interface

3. **Reward Functions** (`instrumentation/reward_functions.py`)
   - Evaluate trace quality
   - Metrics: safety, empathy, length, latency
   - Combined score for training

4. **Training Script** (`scripts/train_agent.py`)
   - Loads and analyzes traces
   - Computes rewards
   - Prepares data for optimization

## Trace Format

Each trace contains:

```json
{
  "trace_id": "Controller_20241206_015930_123456",
  "component": "Controller",
  "timestamp_start": "2024-12-06T01:59:30.123456",
  "timestamp_end": "2024-12-06T01:59:31.456789",
  "prompt": "..."  ,
  "metadata": {
    "model": "llama-3.1-8b-instant",
    "max_tokens": 500,
    "temperature": 0.0
  },
  "response": { ... },
  "latency_ms": 1333.33,
  "reward": 0.85
}
```

## Reward System

Traces are scored on multiple dimensions:

- **Safety** (50%): No policy violations
- **Empathy** (30%): Empathetic tone and language
- **Length** (10%): Appropriate response length (50-200 chars)
- **Latency** (10%): Fast response time (<1s ideal)

Combined score: 0.0 (worst) to 1.0 (best)

## Training Workflows

### Workflow 1: Collect Baseline Traces

```bash
# Enable tracing
export ENABLE_TRACING=true

# Run agent for 100 conversations
python run_agent.py

# Analyze results
python scripts/train_agent.py --mode=analyze
```

### Workflow 2: Prompt Optimization (APO)

```bash
# Analyze traces and find best prompts
python scripts/train_agent.py --mode=apo --output-dir=optimized_prompts

# Review suggested prompts
cat optimized_prompts/top_traces.json
```

### Workflow 3: Date-Filtered Analysis

```bash
# Analyze traces from specific date range
python scripts/train_agent.py \
  --start-date=20241201 \
  --end-date=20241206 \
  --mode=analyze
```

## Integration with Agent-Lightning

The current implementation provides the **foundation** for Agent-Lightning:

1. ✅ Trace collection infrastructure
2. ✅ Reward computation
3. ✅ Data organization
4. 🚧 Full APO integration (requires Agent-Lightning setup)
5. 🚧 RL training workflows (requires Agent-Lightning setup)

### Next Steps for Full Integration

To enable full Agent-Lightning capabilities:

1. **Review Agent-Lightning Examples**
   ```bash
   git clone https://github.com/microsoft/agent-lightning
   cd agent-lightning/examples/apo
   ```

2. **Adapt to Your Traces**
   - Use `TraceStore.load_traces()` to provide data
   - Configure APO algorithm with your prompts
   - Run optimization experiments

3. **Deploy Optimized Prompts**
   - Test in staging environment
   - A/B test against baseline
   - Monitor safety metrics

## Safety Considerations

⚠️ **Important**: Always validate optimized prompts before production deployment.

1. **Test in Isolation**: Run optimized prompts through safety pipeline
2. **A/B Testing**: Deploy to 10% of traffic first
3. **Monitor Metrics**: Watch for any degradation in safety or quality
4. **Rollback Plan**: Keep baseline prompts ready

## Privacy

Traces may contain user messages. For production:

1. **Anonymize**: Strip PII before saving traces
2. **Sampling**: Only trace 10% of conversations
3. **Retention**: Auto-delete traces after 30 days
4. **Access Control**: Restrict trace directory permissions

## Troubleshooting

### No traces being saved?

Check:
```bash
# Is tracing enabled?
echo $ENABLE_TRACING

# Does trace directory exist?
ls -la traces/

# Check for errors in logs
python run_agent.py
```

### Training script fails?

```bash
# Verify traces exist
python scripts/train_agent.py --mode=analyze

# Check trace format
cat traces/*/Controller_*.json | head -n 50
```

## Dashboard (Optional)

Agent-Lightning includes a dashboard for visualizing traces:

```bash
# In agent-lightning repo
cd dashboard
python app.py --trace-dir=/path/to/mhc-agentic/traces
```

Then open `http://localhost:5000` to inspect traces and experiments.

## Performance Impact

Tracing overhead:
- **Memory**: ~1KB per trace
- **Latency**: <5ms per LLM call
- **Disk**: ~10MB per 1000 traces

For production, use **sampling** to reduce overhead:
```python
# In run_agent.py, modify:
import random
enable_tracing = random.random() < 0.1  # 10% sampling
```

## Files Modified/Added

```
mhc-agentic/
├── instrumentation/           [NEW]
│   ├── __init__.py
│   ├── agent_tracing.py      # TracedLLMClient wrapper
│   ├── trace_store.py        # Trace persistence
│   └── reward_functions.py   # Evaluation metrics
├── scripts/                   [NEW]
│   └── train_agent.py        # Training entry point
├── traces/                    [NEW, auto-created]
│   └── YYYYMMDD/
│       └── *.json            # Trace files
├── run_agent.py              [MODIFIED]
│   └── Added tracing wrappers
└── requirements.txt          [MODIFIED]
    └── Added agentlightning
```

## Resources

- [Agent-Lightning Docs](https://microsoft.github.io/agent-lightning/)
- [Agent-Lightning GitHub](https://github.com/microsoft/agent-lightning)
- [APO Paper](https://arxiv.org/abs/2305.03495)
- [This Project's Architecture](ARCHITECTURE_DEEP_DIVE.md)
