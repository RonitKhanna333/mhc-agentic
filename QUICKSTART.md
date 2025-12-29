# Quick Start Guide - Mental Health Chatbot with Agent-Lightning

## Prerequisites

- Python 3.8+
- API key from Groq or Google Gemini
- Git (for cloning)

## Step 1: Setup Environment

```bash
# Clone repository (if not already done)
git clone https://github.com/RonitKhanna333/mhc-agentic.git
cd mhc-agentic

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure API Keys

```bash
# Copy example env file
cp .env.example .env

# Edit .env file and add your API key
# For Groq:
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
GROQ_MASTER_MODEL=llama-3.3-70b-versatile

# For Gemini (alternative):
# LLM_PROVIDER=gemini
# GEMINI_API_KEY=your_gemini_key_here
```

## Step 3: Run Basic Chatbot

```bash
# Run the chatbot
python run_agent.py
```

**What you'll see:**
- Interactive chat interface
- Safety pipeline checking each message
- Tool-based response generation
- Therapeutic responses

**Example conversation:**
```
You: I've been feeling anxious lately
Bot: [Runs safety checks → Emotion analysis → Therapy suggestions → Final response]
Bot: "I hear that anxiety can feel overwhelming. Let's explore what might help..."
```

## Step 4: Enable Tracing (for Agent-Lightning)

```bash
# Edit .env file
ENABLE_TRACING=true

# Run agent again
python run_agent.py
```

**What happens:**
- Every LLM call is recorded as a trace
- Saved to `traces/YYYYMMDD/*.json`
- Includes prompts, responses, latency, metadata

**Have a few conversations** (10-20 messages) to collect traces.

## Step 5: View Trace Statistics

```bash
# Analyze collected traces
python scripts/train_agent.py --mode=analyze
```

**Example output:**
```
Trace Statistics
================
Total traces: 45
Components: {'Controller': 20, 'MasterResponder': 25}
Avg latency: 1234.5ms

Reward Statistics:
  Average: 0.762
  Max: 0.923
  Min: 0.534
```

## Step 6: Run APO (Optimize Prompts)

```bash
# Optimize Controller prompt
python scripts/train_agent.py --mode=apo --output-dir=apo_results
```

**What you'll see:**
```
APO: Automatic Prompt Optimization
===================================
Population size: 8
Generations: 5
Traces: 45

Evaluating Generation 0...
  baseline_v0: avg_reward=0.762 (n=20)
  gen0_variant1: avg_reward=0.781 (n=20)
  gen0_variant2: avg_reward=0.745 (n=20)
  ...

Top 3 in Generation 0:
  1. gen0_variant1: 0.781
  2. baseline_v0: 0.762
  3. gen0_variant4: 0.758

[... more generations ...]

✅ Optimization Complete!
Best Variant: gen4_variant2
Avg Reward: 0.834
Improvement: +9.4%

📁 Results saved to apo_results/
```

**Check results:**
```bash
# View optimized prompt
cat apo_results/best_prompt.txt

# View summary
cat apo_results/optimization_summary.json
```

## Step 7: Run RL Training

```bash
# Learn better tool selection policy
python scripts/train_agent.py --mode=rl
```

**What you'll see:**
```
PPO Training
============
Training on 45 traces
Action space: ['EmotionTool', 'SentimentTool', ...]

Epoch 1/10
  Epoch 1 complete

[... more epochs ...]

📊 Learned Policy Summary:
  Action Usage:
    TherapyTool: 42.3% (avg_adv=0.123)
    EmotionTool: 28.1% (avg_adv=0.098)
    ResourceTool: 15.6% (avg_adv=0.067)
    ...

✅ Training Complete!
💾 Policy saved to learned_policy/learned_policy.json
```

## Step 8: Run Both (APO + RL)

```bash
# Run complete optimization
python scripts/train_agent.py --mode=all
```

This runs APO followed by RL training.

## Step 9: Debug Mode

Want to see what's happening inside?

```bash
# Edit .env
DEBUG_MODE=true

# Run agent
python run_agent.py
```

**You'll see:**
- Safety check results
- Tool selection decisions
- Each tool's output
- Final response construction

## Step 10: Test Tracing

```bash
# Run test script
python tests/test_tracing.py
```

**Expected output:**
```
Testing Agent-Lightning Tracing
================================

1. Creating traced LLM client...
✅ Traced client created

2. Making test LLM call...
✅ LLM call successful

3. Checking trace was saved...
   Total traces: 1
   Components: {'TestComponent': 1}
✅ Trace successfully recorded!

✅ All tests passed!
```

## Common Workflows

### Workflow 1: Basic Usage
```bash
python run_agent.py
# Chat with the bot
```

### Workflow 2: Collect Training Data
```bash
# 1. Enable tracing
export ENABLE_TRACING=true

# 2. Run agent and have conversations
python run_agent.py

# 3. View statistics
python scripts/train_agent.py --mode=analyze
```

### Workflow 3: Full Optimization
```bash
# 1. Collect 50+ conversations with tracing enabled
# 2. Run optimization
python scripts/train_agent.py --mode=all --output-dir=results

# 3. Review results
cat results/optimization_summary.json
cat results/best_prompt.txt
```

## Troubleshooting

### No traces collected?
```bash
# Check if tracing is enabled
grep ENABLE_TRACING .env

# Should show: ENABLE_TRACING=true

# Check traces directory
ls -la traces/
```

### API key not working?
```bash
# Verify key is set
echo $GROQ_API_KEY  # or check .env file

# Test API
python -c "from llm_clients import GroqClient; client = GroqClient(); print(client.generate('Hello', max_tokens=10))"
```

### Import errors?
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
python -c "import agentlightning; print('✅ agentlightning installed')"
```

## What Each File Does

- **`run_agent.py`**: Main chatbot entry point
- **`scripts/train_agent.py`**: Training and optimization
- **`instrumentation/`**: Tracing infrastructure
- **`agent_lightning/`**: APO and RL algorithms
- **`safety/`**: Safety pipeline components
- **`tools/`**: Specialized tools (emotion, therapy, etc.)
- **`core/`**: Controller and orchestration

## Next Steps

1. ✅ Run basic chatbot
2. ✅ Enable tracing and collect data
3. ✅ Run optimization (APO + RL)
4. Review optimized prompts
5. Test in staging environment
6. Deploy with A/B testing (see `PromptRegistry`)

## Getting Help

- **Architecture**: See `ARCHITECTURE_DEEP_DIVE.md`
- **Agent-Lightning**: See `AGENT_LIGHTNING_FULL.md`
- **Safety**: See `ARCHITECTURE_DEEP_DIVE.md` (Stage 1)

## Example Session

```bash
$ python run_agent.py

Mental Health Chatbot (Hybrid Agentic Architecture)
====================================================

You: I'm feeling stressed about work

[Safety Pipeline: ✓ Sanitized ✓ No Crisis ✓ Appropriate]
[Controller: Selected tools - EmotionTool, TherapyTool]
[EmotionTool: Detected 'stress' (0.82), 'anxiety' (0.34)]
[TherapyTool: Retrieved CBT stress management techniques]
[MasterResponder: Synthesizing empathetic response...]

Bot: I can hear the stress in your message. Work pressure can 
feel overwhelming. One thing that helps is breaking tasks into 
smaller pieces - what's one small thing you could tackle today?

You: exit

Session saved to sessions/20241206_021323.json
```

That's it! You're now running a full mental health chatbot with Agent-Lightning optimization capabilities. 🚀
