"""
Trace storage for Agent-Lightning integration.
Manages saving and loading conversation traces.
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class TraceStore:
    """
    Stores and retrieves traces for Agent-Lightning training.
    """
    
    def __init__(self, trace_dir: str = "traces"):
        self.trace_dir = Path(trace_dir)
        self.trace_dir.mkdir(parents=True, exist_ok=True)
        self.active_traces: Dict[str, Dict[str, Any]] = {}
        
    def start_trace(
        self, 
        component: str,
        prompt: str, 
        metadata: Dict[str, Any]
    ) -> str:
        """
        Start a new trace for an LLM call.
        
        Args:
            component: Name of the component making the call (Controller, MasterResponder, etc.)
            prompt: The prompt being sent to the LLM
            metadata: Additional context (model, temperature, etc.)
            
        Returns:
            trace_id: Unique identifier for this trace
        """
        trace_id = f"{component}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        self.active_traces[trace_id] = {
            "trace_id": trace_id,
            "component": component,
            "timestamp_start": datetime.now().isoformat(),
            "prompt": prompt,
            "metadata": metadata,
            "response": None,
            "timestamp_end": None,
            "latency_ms": None,
            "reward": None
        }
        
        return trace_id
    
    def end_trace(
        self,
        trace_id: str,
        response: Any,
        reward: Optional[float] = None
    ):
        """
        Complete a trace with the LLM response.
        
        Args:
            trace_id: The trace ID from start_trace()
            response: The LLM response
            reward: Optional reward signal for training
        """
        if trace_id not in self.active_traces:
            print(f"Warning: trace_id {trace_id} not found in active traces")
            return
        
        trace = self.active_traces[trace_id]
        timestamp_end = datetime.now()
        
        # Calculate latency
        timestamp_start = datetime.fromisoformat(trace["timestamp_start"])
        latency_ms = (timestamp_end - timestamp_start).total_seconds() * 1000
        
        # Update trace
        trace["response"] = response
        trace["timestamp_end"] = timestamp_end.isoformat()
        trace["latency_ms"] = latency_ms
        trace["reward"] = reward
        
        # Save to disk
        self._save_trace(trace)
        
        # Remove from active traces
        del self.active_traces[trace_id]
    
    def _save_trace(self, trace: Dict[str, Any]):
        """Save a completed trace to disk."""
        # Organize by date
        date_str = datetime.now().strftime("%Y%m%d")
        date_dir = self.trace_dir / date_str
        date_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as JSON
        filename = f"{trace['trace_id']}.json"
        filepath = date_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(trace, f, indent=2)
    
    def load_traces(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        component: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Load traces from disk with optional filtering.
        
        Args:
            start_date: Filter traces after this date (YYYYMMDD)
            end_date: Filter traces before this date (YYYYMMDD)
            component: Filter by component name
            
        Returns:
            List of trace dictionaries
        """
        traces = []
        
        # Iterate through date directories
        for date_dir in sorted(self.trace_dir.iterdir()):
            if not date_dir.is_dir():
                continue
            
            date_str = date_dir.name
            
            # Apply date filters
            if start_date and date_str < start_date:
                continue
            if end_date and date_str > end_date:
                continue
            
            # Load all JSON files in this date directory
            for trace_file in date_dir.glob("*.json"):
                with open(trace_file, 'r') as f:
                    trace = json.load(f)
                
                # Apply component filter
                if component and trace.get("component") != component:
                    continue
                
                traces.append(trace)
        
        return traces
    
    def get_trace_stats(self) -> Dict[str, Any]:
        """Get statistics about stored traces."""
        all_traces = self.load_traces()
        
        if not all_traces:
            return {
                "total_traces": 0,
                "components": {},
                "avg_latency_ms": 0
            }
        
        # Count by component
        component_counts = {}
        total_latency = 0
        
        for trace in all_traces:
            comp = trace.get("component", "unknown")
            component_counts[comp] = component_counts.get(comp, 0) + 1
            total_latency += trace.get("latency_ms", 0)
        
        return {
            "total_traces": len(all_traces),
            "components": component_counts,
            "avg_latency_ms": total_latency / len(all_traces) if all_traces else 0
        }
