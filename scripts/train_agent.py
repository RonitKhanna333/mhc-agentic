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
    print("\n" + "="*60)
    print("Running APO (Automatic Prompt Optimization)")
    print("="*60)
    
    # TODO: integrate with Agent-Lightning APO algorithm
    # This is a placeholder showing the structure
    
    print(f"\nNote: Full APO integration requires Agent-Lightning setup.")
    print(f"See examples at: https://microsoft.github.io/agent-lightning/")
    
    # For now, just analyze which prompts perform best
    controller_traces = [t for t in traces if t.get("component") == "Controller"]
    responder_traces = [t for t in traces if t.get("component") == "MasterResponder"]
    
    print(f"\nController traces: {len(controller_traces)}")
    print(f"MasterResponder traces: {len(responder_traces)}")
    
    if controller_traces:
        avg_controller_reward = sum(t["reward"] for t in controller_traces) / len(controller_traces)
        print(f"Avg Controller reward: {avg_controller_reward:.3f}")
    
    if responder_traces:
        avg_responder_reward = sum(t["reward"] for t in responder_traces) / len(responder_traces)
        print(f"Avg MasterResponder reward: {avg_responder_reward:.3f}")
    
    # Save best-performing prompts for manual inspection
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Find top 10 best traces
    top_traces = sorted(traces, key=lambda t: t.get("reward", 0), reverse=True)[:10]
    
    print(f"\nTop 10 traces saved to {output_dir}/top_traces.json")
    import json
    with open(f"{output_dir}/top_traces.json", "w") as f:
        json.dump(top_traces, f, indent=2)
    
    print("\n✅ Analysis complete!")


def main():
    parser = argparse.ArgumentParser(description="Train agent with Agent-Lightning")
    parser.add_argument("--trace-dir", default="traces", help="Directory containing traces")
    parser.add_argument("--start-date", help="Start date filter (YYYYMMDD)")
    parser.add_argument("--end-date", help="End date filter (YYYYMMDD)")
    parser.add_argument("--output-dir", default="optimized_prompts", help="Output directory")
    parser.add_argument("--mode", choices=["apo", "rl", "analyze"], default="analyze",
                       help="Training mode: apo=prompt optimization, rl=policy learning, analyze=stats only")
    
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
    if args.mode == "apo":
        run_apo_training(scored_traces, output_dir=args.output_dir)
    elif args.mode == "rl":
        print("\n🚧 RL training not yet implemented")
        print("This would use Agent-Lightning's RL algorithms")
    elif args.mode == "analyze":
        print("\n✅ Analysis complete. Use --mode=apo to run optimization.")


if __name__ == "__main__":
    main()
