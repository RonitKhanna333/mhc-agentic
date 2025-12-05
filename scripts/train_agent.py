"""
Training script for Agent-Lightning integration.
Loads traces and runs optimization algorithms.
"""
import os
import argparse
from pathlib import Path
from instrumentation import TraceStore
from instrumentation.reward_functions import compute_combined_reward


def compute_rewards_for_traces(trace_store: TraceStore, start_date=None, end_date=None):
    """
    Load traces and compute rewards for each.
    
    Args:
        trace_store: TraceStore instance
        start_date: Optional start date filter (YYYYMMDD)
        end_date: Optional end date filter (YYYYMMDD)
    """
    print("Loading traces...")
    traces = trace_store.load_traces(start_date=start_date, end_date=end_date)
    print(f"Loaded {len(traces)} traces")
    
    if not traces:
        print("No traces found. Run the agent with ENABLE_TRACING=true to collect traces.")
        return []
    
    print("\nComputing rewards...")
    scored_traces = []
    
    for trace in traces:
        reward = compute_combined_reward(trace)
        trace["reward"] = reward
        scored_traces.append(trace)
    
    # Print statistics
    avg_reward = sum(t["reward"] for t in scored_traces) / len(scored_traces)
    max_reward = max(t["reward"] for t in scored_traces)
    min_reward = min(t["reward"] for t in scored_traces)
    
    print(f"\nReward Statistics:")
    print(f"  Average: {avg_reward:.3f}")
    print(f"  Max: {max_reward:.3f}")
    print(f"  Min: {min_reward:.3f}")
    
    return scored_traces


def run_apo_training(traces, output_dir="optimized_prompts"):
    """
    Run Automatic Prompt Optimization using Agent-Lightning.
    
    Args:
        traces: List of traces with rewards
        output_dir: Where to save optimized prompts
    """
    from agent_lightning import APOOptimizer
    from core.controller import Controller
    
    print("\n" + "="*60)
    print("Running APO (Automatic Prompt Optimization)")
    print("="*60)
    
    # Get baseline Controller prompt
    # This is the prompt we want to optimize
    controller = Controller(None, {})
    baseline_prompt = controller.system_prompt
    
    # Filter traces by component
    controller_traces = [t for t in traces if t.get("component") == "Controller"]
    
    if not controller_traces:
        print("❌ No Controller traces found. Run agent with tracing enabled first.")
        return
    
    print(f"\nOptimizing Controller prompt using {len(controller_traces)} traces")
    
    # Initialize APO optimizer
    optimizer = APOOptimizer(
        baseline_prompt=baseline_prompt,
        population_size=8,
        num_generations=5,
        mutation_rate=0.3
    )
    
    # Run optimization
    best_variant = optimizer.optimize(controller_traces)
    
    # Save results
    optimizer.save_results(output_dir)
    
    # Compare baseline vs optimized
    print("\n📊 Comparison:")
    print(f"  Baseline: {optimizer.population[0].avg_reward:.3f}")
    print(f"  Optimized: {best_variant.avg_reward:.3f}")
    print(f"  Improvement: +{(best_variant.avg_reward - optimizer.population[0].avg_reward)*100:.1f}%")
    
    print(f"\n💾 Best prompt saved to: {output_dir}/best_prompt.txt")
    print(f"📊 Full results in: {output_dir}/")
    
    return best_variant


def run_rl_training(traces, output_dir="learned_policy"):
    """
    Run RL training to learn better tool selection policy.
    
    Args:
        traces: List of traces with rewards
        output_dir: Where to save learned policy
    """
    from agent_lightning import PPOTrainer
    
    print("\n" + "="*60)
    print("Running RL Training (PPO)")
    print("="*60)
    
    # Define action space (tools that Controller can select)
    action_space = [
        "EmotionTool",
        "SentimentTool",
        "PatternDetectorTool",
        "MemoryReadTool",
        "TherapyTool",
        "ResourceTool",
        "AssessmentTool",
        "InterventionSelectorTool"
    ]
    
    # Initialize PPO trainer
    trainer = PPOTrainer(
        action_space=action_space,
        learning_rate=0.0003,
        gamma=0.99,
        epsilon=0.2,
        num_epochs=10
    )
    
    # Train on traces
    trainer.train_on_traces(traces)
    
    # Save learned policy
    trainer.save_policy(output_dir)
    
    print(f"\n💾 Policy saved to: {output_dir}/learned_policy.json")
    
    return trainer


def main():
    parser = argparse.ArgumentParser(description="Train agent with Agent-Lightning")
    parser.add_argument("--trace-dir", default="traces", help="Directory containing traces")
    parser.add_argument("--start-date", help="Start date filter (YYYYMMDD)")
    parser.add_argument("--end-date", help="End date filter (YYYYMMDD)")
    parser.add_argument("--output-dir", default="optimized_prompts", help="Output directory")
    parser.add_argument("--mode", choices=["apo", "rl", "analyze", "all"], default="analyze",
                       help="Training mode: apo=prompt optimization, rl=policy learning, analyze=stats only, all=run both")
    
    args = parser.parse_args()
    
    # Initialize trace store
    trace_store = TraceStore(trace_dir=args.trace_dir)
    
    # Show trace statistics
    stats = trace_store.get_trace_stats()
    print("\n" + "="*60)
    print("Trace Statistics")
    print("="*60)
    print(f"Total traces: {stats['total_traces']}")
    print(f"Components: {stats['components']}")
    print(f"Avg latency: {stats['avg_latency_ms']:.1f}ms")
    
    if stats['total_traces'] == 0:
        print("\n❌ No traces found!")
        print("Run the agent with ENABLE_TRACING=true to collect traces first.")
        return
    
    # Compute rewards
    scored_traces = compute_rewards_for_traces(
        trace_store, 
        start_date=args.start_date,
        end_date=args.end_date
    )
    
    # Run training based on mode
    if args.mode == "apo" or args.mode == "all":
        run_apo_training(scored_traces, output_dir=args.output_dir)
    
    if args.mode == "rl" or args.mode == "all":
        run_rl_training(scored_traces, output_dir="learned_policy")
    
    if args.mode == "analyze":
        print("\n✅ Analysis complete. Use --mode=apo or --mode=rl to run optimization.")


if __name__ == "__main__":
    main()
