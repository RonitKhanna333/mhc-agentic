"""
RL training using PPO (Proximal Policy Optimization).
Trains the Controller to select better tool sequences.
"""
import json
import numpy as np
from typing import List, Dict, Any, Tuple
from pathlib import Path


class PolicyState:
    """Represents a state in the RL environment."""
    
    def __init__(self, user_message: str, risk_level: str, session_summary: str):
        self.user_message = user_message
        self.risk_level = risk_level
        self.session_summary = session_summary
    
    def to_features(self) -> np.ndarray:
        """Convert to feature vector for policy network."""
        # Simplified feature extraction
        features = []
        
        # Message length
        features.append(len(self.user_message) / 500.0)
        
        # Risk level encoding
        risk_encoding = {"high": 1.0, "medium": 0.5, "none": 0.0}
        features.append(risk_encoding.get(self.risk_level, 0.0))
        
        # Has session history
        features.append(1.0 if self.session_summary else 0.0)
        
        # Emotion keywords
        emotion_words = ["sad", "angry", "anxious", "hopeless", "happy", "excited"]
        for word in emotion_words:
            features.append(1.0 if word in self.user_message.lower() else 0.0)
        
        return np.array(features, dtype=np.float32)


class PolicyAction:
    """Represents an action (tool sequence decision)."""
    
    def __init__(self, tool_sequence: List[str]):
        self.tool_sequence = tool_sequence
    
    def to_index(self, action_space: List[str]) -> int:
        """Convert to action index."""
        # Simplified: use first tool as action
        if self.tool_sequence:
            try:
                return action_space.index(self.tool_sequence[0])
            except ValueError:
                return 0
        return 0


class PPOTrainer:
    """
    Proximal Policy Optimization trainer for Controller.
    
    Trains the Controller to select better tool sequences
    based on reward signals.
    """
    
    def __init__(
        self,
        action_space: List[str],
        learning_rate: float = 0.0003,
        gamma: float = 0.99,
        epsilon: float = 0.2,
        num_epochs: int = 10
    ):
        self.action_space = action_space
        self.learning_rate = learning_rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # PPO clip parameter
        self.num_epochs = num_epochs
        
        # Policy statistics
        self.action_counts = {action: 0 for action in action_space}
        self.action_rewards = {action: [] for action in action_space}
    
    def compute_advantages(
        self, 
        rewards: List[float], 
        values: List[float]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).
        
        Args:
            rewards: List of rewards for each step
            values: List of value estimates for each state
            
        Returns:
            advantages: Advantage estimates
            returns: Discounted returns
        """
        advantages = np.zeros(len(rewards))
        returns = np.zeros(len(rewards))
        
        # Compute returns
        running_return = 0
        for t in reversed(range(len(rewards))):
            running_return = rewards[t] + self.gamma * running_return
            returns[t] = running_return
        
        # Compute advantages (returns - value estimates)
        advantages = returns - np.array(values)
        
        # Normalize advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        return advantages, returns
    
    def train_on_traces(self, traces: List[Dict[str, Any]]):
        """
        Train policy on collected traces.
        
        Args:
            traces: List of trace dicts from TraceStore
        """
        print("="*60)
        print("PPO Training")
        print("="*60)
        print(f"Training on {len(traces)} traces")
        print(f"Action space: {self.action_space}")
        
        # Extract episodes from traces
        episodes = self._traces_to_episodes(traces)
        print(f"Extracted {len(episodes)} episodes")
        
        # Train for multiple epochs
        for epoch in range(self.num_epochs):
            print(f"\nEpoch {epoch+1}/{self.num_epochs}")
            
            epoch_loss = 0
            for episode in episodes:
                # Compute advantages
                rewards = [step['reward'] for step in episode]
                values = [step.get('value', 0.5) for step in episode]  # Placeholder values
                
                advantages, returns = self.compute_advantages(rewards, values)
                
                # Update statistics
                for step, adv in zip(episode, advantages):
                    action = step['action']
                    if action in self.action_space:
                        self.action_counts[action] += 1
                        self.action_rewards[action].append(adv)
            
            print(f"  Epoch {epoch+1} complete")
        
        # Print learned policy
        self._print_policy_summary()
        
        print("\n" + "="*60)
        print("✅ Training Complete!")
        print("="*60)
    
    def _traces_to_episodes(self, traces: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Convert traces to episodes for training."""
        episodes = []
        
        for trace in traces:
            # Each trace is one step in an episode
            # In a full implementation, would group by conversation
            episode = [{
                'state': trace.get('prompt', ''),
                'action': self._extract_action(trace),
                'reward': trace.get('reward', 0.0),
                'next_state': None
            }]
            episodes.append(episode)
        
        return episodes
    
    def _extract_action(self, trace: Dict[str, Any]) -> str:
        """Extract action (tool used) from trace."""
        component = trace.get('component', 'unknown')
        
        # Map component to action space
        if component == "Controller":
            return "EmotionTool"  # Placeholder
        elif component == "MasterResponder":
            return "MasterResponderTool"
        else:
            return self.action_space[0] if self.action_space else "unknown"
    
    def _print_policy_summary(self):
        """Print learned policy statistics."""
        print("\n📊 Learned Policy Summary:")
        print("  Action Usage:")
        total_actions = sum(self.action_counts.values())
        for action, count in sorted(self.action_counts.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total_actions * 100) if total_actions > 0 else 0
            avg_reward = np.mean(self.action_rewards[action]) if self.action_rewards[action] else 0
            print(f"    {action}: {pct:.1f}% (avg_adv={avg_reward:.3f})")
    
    def save_policy(self, output_dir: str):
        """Save learned policy."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        policy_data = {
            "action_space": self.action_space,
            "action_counts": self.action_counts,
            "action_avg_rewards": {
                action: float(np.mean(rewards)) if rewards else 0.0
                for action, rewards in self.action_rewards.items()
            },
            "hyperparameters": {
                "learning_rate": self.learning_rate,
                "gamma": self.gamma,
                "epsilon": self.epsilon,
                "num_epochs": self.num_epochs
            }
        }
        
        with open(output_path / "learned_policy.json", "w") as f:
            json.dump(policy_data, f, indent=2)
        
        print(f"\n📁 Policy saved to {output_dir}/learned_policy.json")
