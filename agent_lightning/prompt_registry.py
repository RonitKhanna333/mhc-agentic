"""
Prompt management system for A/B testing and rollout.
"""
import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class PromptRegistry:
    """
    Manages different prompt versions and enables A/B testing.
    """
    
    def __init__(self, registry_file: str = "prompts/registry.json"):
        self.registry_file = Path(registry_file)
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing registry
        if self.registry_file.exists():
            with open(self.registry_file, "r") as f:
                self.registry = json.load(f)
        else:
            self.registry = {
                "prompts": {},
                "active_variant": "baseline",
                "ab_test": None
            }
    
    def register_prompt(
        self, 
        variant_id: str,
        component: str,
        content: str,
        metadata: Dict[str, Any] = None
    ):
        """Register a new prompt variant."""
        if component not in self.registry["prompts"]:
            self.registry["prompts"][component] = {}
        
        self.registry["prompts"][component][variant_id] = {
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "performance": {
                "total_uses": 0,
                "avg_reward": 0.0,
                "rewards": []
            }
        }
        
        self._save()
    
    def get_prompt(self, component: str, variant_id: str = None) -> str:
        """
        Get prompt for a component.
        
        Args:
            component: Component name (e.g., "Controller", "MasterResponder")
            variant_id: Specific variant ID, or None for active variant
            
        Returns:
            Prompt content
        """
        if variant_id is None:
            # Use active variant
            variant_id = self.registry["active_variant"]
        
        if component not in self.registry["prompts"]:
            raise ValueError(f"Component {component} not found in registry")
        
        if variant_id not in self.registry["prompts"][component]:
            # Fall back to baseline
            variant_id = "baseline"
        
        return self.registry["prompts"][component][variant_id]["content"]
    
    def record_performance(
        self,
        component: str,
        variant_id: str,
        reward: float
    ):
        """Record performance for a prompt variant."""
        if component in self.registry["prompts"] and variant_id in self.registry["prompts"][component]:
            perf = self.registry["prompts"][component][variant_id]["performance"]
            perf["total_uses"] += 1
            perf["rewards"].append(reward)
            perf["avg_reward"] = sum(perf["rewards"]) / len(perf["rewards"])
            
            self._save()
    
    def start_ab_test(
        self,
        component: str,
        variant_a: str,
        variant_b: str,
        traffic_split: float = 0.5
    ):
        """
        Start an A/B test between two variants.
        
        Args:
            component: Component to test
            variant_a: First variant ID
            variant_b: Second variant ID
            traffic_split: Fraction of traffic to variant_b (0.0 to 1.0)
        """
        self.registry["ab_test"] = {
            "component": component,
            "variant_a": variant_a,
            "variant_b": variant_b,
            "traffic_split": traffic_split,
            "started_at": datetime.now().isoformat()
        }
        
        self._save()
        print(f"✅ A/B Test started: {variant_a} vs {variant_b} ({traffic_split*100}% to B)")
    
    def stop_ab_test(self, winner: str = None):
        """
        Stop A/B test and optionally set winner as active.
        
        Args:
            winner: Variant ID to make active, or None to keep current
        """
        if self.registry["ab_test"]:
            component = self.registry["ab_test"]["component"]
            variant_a = self.registry["ab_test"]["variant_a"]
            variant_b = self.registry["ab_test"]["variant_b"]
            
            # Get performance
            perf_a = self.registry["prompts"][component][variant_a]["performance"]["avg_reward"]
            perf_b = self.registry["prompts"][component][variant_b]["performance"]["avg_reward"]
            
            print("\n📊 A/B Test Results:")
            print(f"  {variant_a}: {perf_a:.3f}")
            print(f"  {variant_b}: {perf_b:.3f}")
            
            if winner:
                self.registry["active_variant"] = winner
                print(f"✅ Winner: {winner} is now active")
            
            self.registry["ab_test"] = None
            self._save()
    
    def _save(self):
        """Save registry to disk."""
        with open(self.registry_file, "w") as f:
            json.dump(self.registry, f, indent=2)
    
    def export_summary(self, output_file: str = "prompts/summary.md"):
        """Export prompt performance summary."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        lines = ["# Prompt Registry Summary\n\n"]
        
        for component, variants in self.registry["prompts"].items():
            lines.append(f"## {component}\n\n")
            
            for variant_id, variant_data in variants.items():
                perf = variant_data["performance"]
                lines.append(f"### {variant_id}\n")
                lines.append(f"- **Uses**: {perf['total_uses']}\n")
                lines.append(f"- **Avg Reward**: {perf['avg_reward']:.3f}\n")
                lines.append(f"- **Created**: {variant_data.get('created_at', 'unknown')}\n\n")
        
        with open(output_path, "w") as f:
            f.writelines(lines)
        
        print(f"📄 Summary exported to {output_file}")
