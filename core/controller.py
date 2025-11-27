import json
from typing import Dict, Any, List
from tools import *

class Controller:
    """
    Stage 2: Agentic Controller.
    Decides which tools to call based on the user's message and safety status.
    """
    
    def __init__(self, llm_client, tool_registry: Dict[str, BaseTool]):
        self.llm = llm_client
        self.tool_registry = tool_registry
        self.system_prompt = """You are the Controller Agent for a mental health support chatbot.
ROLE: Decide which tools to call to best respond to the user's message.
CONSTRAINTS:
- Safety checks (crisis, moderation) ALREADY RAN - you cannot bypass them
- You may call ANY tool from the registry EXCEPT system-only tools
- Output ONLY valid JSON (no markdown, no explanations outside JSON)
- Prefer fewer tool calls if not needed
- Always end with "MasterResponderTool" as final_action

AVAILABLE TOOLS:
{tool_descriptions}

INPUT:
{{
"user_message": {{user_message_text}},
"risk_level": {{risk_level}},
"session_summary": {{session_summary}}
}}

TASK:
Analyze the user's message and decide which tools to call.

OUTPUT FORMAT (JSON only):
{{
"tool_sequence": [
{{"name": "ToolName1", "input": {{...}}, "reason": "why calling this"}},
{{"name": "ToolName2", "input": {{...}}, "reason": "why calling this"}}
],
"final_action": "MasterResponderTool",
"overall_strategy": "brief 1-sentence explanation of approach"
}}
"""

    def _get_tool_descriptions(self) -> str:
        descriptions = []
        for name, tool in self.tool_registry.items():
            descriptions.append(f"- {name}: {tool.description}")
        return "\n".join(descriptions)

    def decide(self, user_input: str, risk_level: str, session_summary: str) -> Dict[str, Any]:
        """
        Decide on the tool sequence.
        """
        tool_desc = self._get_tool_descriptions()
        prompt = self.system_prompt.format(
            tool_descriptions=tool_desc,
            user_message_text=json.dumps(user_input),
            risk_level=risk_level,
            session_summary=session_summary
        )
        
        response = self.llm.generate(prompt, max_tokens=500, temperature=0.0) # Low temp for deterministic JSON
        
        text = ""
        if isinstance(response, dict):
             if 'choices' in response and response['choices']:
                text = response['choices'][0]['message']['content']
             elif 'candidates' in response and response['candidates']:
                text = response['candidates'][0]['content']['parts'][0]['text']
        else:
            text = str(response)
            
        # Clean up markdown code blocks if present
        text = text.replace("```json", "").replace("```", "").strip()
        
        try:
            plan = json.loads(text)
            return plan
        except json.JSONDecodeError:
            # Fallback plan if JSON fails
            print(f"Error parsing JSON plan: {text}")
            return {
                "tool_sequence": [],
                "final_action": "MasterResponderTool",
                "overall_strategy": "Fallback: Direct response due to parse error"
            }
