"""
Test script for Agent-Lightning integration.
Verifies tracing works correctly.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from instrumentation import TraceStore, create_traced_client
from llm_clients import GroqClient


def test_tracing():
    """Test basic tracing functionality."""
    print("=" * 60)
    print("Testing Agent-Lightning Tracing")
    print("=" * 60)
    
    # Enable tracing for this test
    os.environ["ENABLE_TRACING"] = "true"
    
    # Create a test trace store
    trace_store = TraceStore(trace_dir="test_traces")
    
    print("\n1. Creating traced LLM client...")
    base_client = GroqClient()
    traced_client = create_traced_client(
        base_client, 
        component_name="TestComponent",
        trace_store=trace_store
    )
    print("✅ Traced client created")
    
    print("\n2. Making test LLM call...")
    try:
        response = traced_client.generate(
            prompt="Say 'Hello, World!' in exactly 3 words.",
            max_tokens=50,
            temperature=0.0
        )
        print("✅ LLM call successful")
        print(f"   Response: {response}")
    except Exception as e:
        print(f"❌ LLM call failed: {e}")
        print("   Note: You may need to set GROQ_API_KEY in .env")
        return False
    
    print("\n3. Checking trace was saved...")
    stats = trace_store.get_trace_stats()
    print(f"   Total traces: {stats['total_traces']}")
    print(f"   Components: {stats['components']}")
    
    if stats['total_traces'] > 0:
        print("✅ Trace successfully recorded!")
        
        # Load and inspect trace
        traces = trace_store.load_traces(component="TestComponent")
        if traces:
            trace = traces[0]
            print(f"\n4. Trace details:")
            print(f"   Trace ID: {trace.get('trace_id')}")
            print(f"   Latency: {trace.get('latency_ms', 0):.1f}ms")
            print(f"   Model: {trace.get('metadata', {}).get('model')}")
    else:
        print("❌ No trace found!")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    print(f"\nTraces saved to: {trace_store.trace_dir}")
    print("You can analyze them with:")
    print("  python scripts/train_agent.py --trace-dir=test_traces --mode=analyze")
    
    return True


if __name__ == "__main__":
    success = test_tracing()
    sys.exit(0 if success else 1)
