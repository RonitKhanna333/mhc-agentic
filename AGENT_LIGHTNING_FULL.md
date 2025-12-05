# Full Agent-Lightning Implementation

## Overview

This implementation includes **complete** APO (Automatic Prompt Optimization) and RL (Reinforcement Learning) training capabilities.

## What's Included

### 1. APO (Automatic Prompt Optimization)

**File**: `agent_lightning/apo_optimizer.py`

**Algorithm**: Evolutionary optimization with:
- Population-based search
- Mutation strategies (add_emphasis, add_constraint, reorder, add_example, simplify)
- Multi-generational evolution
- Automatic evaluation on historical traces
- Best variant selection

**Usage**:
```bash
python scripts/train_agent.py --mode=apo --output-dir=optimized_prompts
```

**Output**:
- `optimized_prompts/best_prompt.txt` - Best performing prompt
- `optimized_prompts/all_variants.json` - All tested variants
- `optimized_prompts/optimization_summary.json` - Statistics

### 2. RL Training (PPO)

**File**: `agent_lightning/ppo_trainer.py`

**Algorithm**: Proximal Policy Optimization with:
- Advantage computation using GAE (Generalized Advantage Estimation)
- Multi-epoch training
- Action space over available tools
- Policy gradient updates
- Performance tracking per action

**Usage**:
```bash
python scripts/train_agent.py --mode=rl --output-dir=learned_policy
```

**Output**:
- `learned_policy/learned_policy.json` - Policy statistics
- Action usage frequencies
- Average advantage per action

### 3. Prompt Management

**File**: `agent_lightning/prompt_registry.py`

**Features**:
- Prompt versioning
- A/B testing framework
- Performance tracking
- Gradual rollout support

**Usage**:
```python
from agent_lightning import PromptRegistry

registry = PromptRegistry()
registry.register_prompt("variant_1", "Controller", new_prompt)
registry.start_ab_test("Controller", "baseline", "variant_1", traffic_split=0.5)
# ... run agent ...
registry.stop_ab_test(winner="variant_1")
```

## Full Workflow

### Step 1: Collect Traces

```bash
# Enable tracing
export ENABLE_TRACING=true

# Run agent to collect data
python run_agent.py
```

### Step 2: Run Optimization

```bash
# Run APO to optimize prompts
python scripts/train_agent.py --mode=apo --output-dir=apo_results

# Run RL to learn policy
python scripts/train_agent.py --mode=rl --output-dir=rl_results

# Or run both
python scripts/train_agent.py --mode=all
```

### Step 3: Review Results

```bash
# Check APO results
cat apo_results/optimization_summary.json
cat apo_results/best_prompt.txt

# Check RL results
cat rl_results/learned_policy.json
```

### Step 4: Deploy (Safe Rollout)

```bash
# 1. Test optimized prompt in staging
# 2. A/B test at 10% traffic
# 3. Monitor safety metrics
# 4. Gradual rollout to 100%
```

## Algorithm Details

### APO Evolution Process

1. **Initialize**: Create baseline + random variants
2. **Evaluate**: Run each variant on historical traces
3. **Select**: Keep top-3 performers
4. **Mutate**: Generate new variants from top performers
5. **Repeat**: Run for N generations

**Mutation Strategies**:
- `add_emphasis`: Add importance markers to instructions
- `add_constraint`: Add new requirements (length, tone, etc.)
- `reorder_instructions`: Shuffle instruction order
- `add_example`: Provide concrete examples
- `simplify`: Remove some instructions

### PPO Training Process

1. **Extract Episodes**: Convert traces to state-action-reward tuples
2. **Compute Advantages**: Use GAE to estimate action quality
3. **Update Policy**: Learn which actions lead to higher rewards
4. **Track Statistics**: Monitor action frequencies and performance

## Advanced Features

### Custom Mutation Strategies

You can add custom mutations in `apo_optimizer.py`:

```python
def _mutate_prompt(self, prompt, strategy):
    if strategy == "my_custom_strategy":
        # Your mutation logic
        return modified_prompt
```

### Custom Reward Functions

Add new reward signals in `instrumentation/reward_functions.py`:

```python
def compute_custom_reward(trace):
    # Your reward logic
    return score
```

## Performance Metrics

### APO Metrics
- Baseline reward
- Optimized reward
- Improvement percentage
- Number of generations
- Population size

### RL Metrics
- Action usage frequencies
- Average advantage per action
- Policy entropy
- Training epochs

## Safety Considerations

⚠️ **Always validate before production**:

1. **Manual Review**: Read optimized prompts
2. **Safety Testing**: Run through safety pipeline
3. **A/B Testing**: Test at 10% traffic first
4. **Monitor**: Watch for degradation in safety metrics
5. **Rollback Plan**: Keep baseline ready

## Limitations

### Current Implementation

- **APO**: Uses heuristic mutations (production would use LLM-based rewriting)
- **PPO**: Simplified policy network (production would use neural networks)
- **Evaluation**: Simulated re-runs (production would actually re-run agent)

### Production Enhancements

For production deployment, consider:
1. Using LLM-based prompt mutations
2. Implementing neural policy networks
3. Adding online learning capabilities
4. Implementing automatic safety checks

## Files Created

```
agent_lightning/
├── __init__.py
├── apo_optimizer.py      (300+ lines) - Evolutionary prompt optimization
├── ppo_trainer.py        (200+ lines) - RL training with PPO
└── prompt_registry.py    (180+ lines) - A/B testing and versioning

scripts/
└── train_agent.py        (Modified) - Integrated APO and RL workflows
```

## Next Steps

1. Collect 500+ traces with `ENABLE_TRACING=true`
2. Run `--mode=all` to optimize both prompts and policy
3. Review results and test in staging
4. Use `PromptRegistry` for safe A/B testing
5. Monitor performance and iterate

## Resources

- [APO Paper](https://arxiv.org/abs/2305.03495)
- [PPO Paper](https://arxiv.org/abs/1707.06347)
- [Agent-Lightning Docs](https://microsoft.github.io/agent-lightning/)
