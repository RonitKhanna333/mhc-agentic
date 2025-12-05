"""
Lightweight tracing wrapper for LLM clients.
Integrates with Agent-Lightning for optimization and training.
"""
import os
from typing import Dict, Any, Optional
from instrumentation.trace_store import TraceStore


class TracedLLMClient:
    """
    Wraps an LLM client to trace all generate() calls.
    This enables Agent-Lightning to collect training data.
    """
    
    def __init__(
        self, 
        base_client, 
        component_name: str,
        trace_store: Optional[TraceStore] = None,
        enabled: bool = None
    ):
        """
        Args:
            base_client: The underlying LLMClient (GroqClient or GeminiClient)
            component_name: Name of the component using this client (e.g., "Controller", "MasterResponder")
            trace_store: TraceStore instance for saving traces
            enabled: Whether tracing is enabled (defaults to env var ENABLE_TRACING)
        """
        self.client = base_client
        self.component_name = component_name
        self.trace_store = trace_store or TraceStore()
        
        # Check if tracing is enabled
        if enabled is None:
            enabled = os.getenv("ENABLE_TRACING", "false").lower() == "true"
        self.enabled = enabled
    
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate LLM response with optional tracing.
        
        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional arguments (max_tokens, temperature, messages, etc.)
            
        Returns:
            LLM response (same format as base client)
        """
        # If tracing is disabled, just pass through
        if not self.enabled:
            return self.client.generate(prompt, **kwargs)
        
        # Start trace
        metadata = {
            "model": getattr(self.client, "model", "unknown"),
            "max_tokens": kwargs.get("max_tokens", None),
            "temperature": kwargs.get("temperature", None),
            "has_messages": "messages" in kwargs
        }
        
        trace_id = self.trace_store.start_trace(
            component=self.component_name,
            prompt=prompt,
            metadata=metadata
        )
        
        try:
            # Call actual LLM
            response = self.client.generate(prompt, **kwargs)
            
            # End trace (reward will be computed later)
            self.trace_store.end_trace(
                trace_id=trace_id,
                response=response,
                reward=None  # Will be updated by reward function
            )
            
            return response
            
        except Exception as e:
            # Log error in trace
            self.trace_store.end_trace(
                trace_id=trace_id,
                response={"error": str(e)},
                reward=-1.0  # Negative reward for errors
            )
            raise
    
    def __getattr__(self, name):
        """
        Proxy other attributes to the base client.
        This allows TracedLLMClient to be used as a drop-in replacement.
        """
        return getattr(self.client, name)


def create_traced_client(
    base_client,
    component_name: str,
    trace_store: Optional[TraceStore] = None
):
    """
    Factory function to create a traced client.
    
    Usage:
        llm = create_traced_client(GroqClient(), "Controller")
    """
    return TracedLLMClient(
        base_client=base_client,
        component_name=component_name,
        trace_store=trace_store
    )
