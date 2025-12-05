"""
Reward functions for Agent-Lightning training.
These functions evaluate the quality of agent responses.
"""
from typing import Dict, Any


def compute_safety_reward(trace: Dict[str, Any]) -> float:
    """
    Reward based on safety compliance.
    
    High reward if no safety violations detected.
    Low reward if OutputScrubber blocks response.
    """
    response = trace.get("response", {})
    
    # Check if response contains error
    if "error" in response:
        return -1.0
    
    # Check if response was blocked by safety (this would be in metadata)
    metadata = trace.get("metadata", {})
    if metadata.get("blocked_by_safety", False):
        return 0.0
    
    # Safe response gets full reward
    return 1.0


def compute_empathy_reward(trace: Dict[str, Any]) -> float:
    """
    Reward based on empathetic tone (heuristic-based for now).
    
    Could be replaced with LLM-as-judge in the future.
    """
    response = trace.get("response", {})
    
    # Extract text from response
    text = ""
    if isinstance(response, dict):
        if 'choices' in response and response['choices']:
            text = response['choices'][0]['message']['content']
        elif 'candidates' in response and response['candidates']:
            text = response['candidates'][0]['content']['parts'][0]['text']
    
    if not text:
        return 0.0
    
    # Simple heuristic: check for empathetic phrases
    empathetic_phrases = [
        "I understand", "I hear you", "that sounds difficult",
        "it makes sense", "I'm here", "you're not alone",
        "that must feel", "it's valid to feel"
    ]
    
    text_lower = text.lower()
    matches = sum(1 for phrase in empathetic_phrases if phrase in text_lower)
    
    # Normalize to 0-1
    return min(matches / 3.0, 1.0)


def compute_length_reward(trace: Dict[str, Any]) -> float:
    """
    Reward for appropriate response length.
    
    Too short = not helpful
    Too long = overwhelming
    Sweet spot = 50-200 characters
    """
    response = trace.get("response", {})
    
    # Extract text from response
    text = ""
    if isinstance(response, dict):
        if 'choices' in response and response['choices']:
            text = response['choices'][0]['message']['content']
        elif 'candidates' in response and response['candidates']:
            text = response['candidates'][0]['content']['parts'][0]['text']
    
    if not text:
        return 0.0
    
    length = len(text)
    
    # Reward function: peaks at 100-150 chars
    if length < 20:
        return 0.2
    elif length < 50:
        return 0.6
    elif 50 <= length <= 200:
        return 1.0
    elif length <= 300:
        return 0.8
    else:
        return 0.5  # Too long


def compute_latency_reward(trace: Dict[str, Any]) -> float:
    """
    Reward for fast response times.
    """
    latency_ms = trace.get("latency_ms", 0)
    
    if latency_ms == 0:
        return 0.0
    
    # Ideal: < 1000ms
    # Acceptable: < 3000ms
    # Slow: > 3000ms
    if latency_ms < 1000:
        return 1.0
    elif latency_ms < 3000:
        return 0.7
    elif latency_ms < 5000:
        return 0.4
    else:
        return 0.1


def compute_combined_reward(trace: Dict[str, Any]) -> float:
    """
    Combine all reward signals into a single score.
    
    Weights:
    - Safety: 50% (critical)
    - Empathy: 30% (important)
    - Length: 10%
    - Latency: 10%
    """
    safety = compute_safety_reward(trace)
    empathy = compute_empathy_reward(trace)
    length = compute_length_reward(trace)
    latency = compute_latency_reward(trace)
    
    # If safety is 0 or negative, heavily penalize
    if safety <= 0:
        return safety
    
    # Weighted combination
    combined = (
        0.5 * safety +
        0.3 * empathy +
        0.1 * length +
        0.1 * latency
    )
    
    return combined
