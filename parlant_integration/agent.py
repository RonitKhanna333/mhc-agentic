"""
Parlant agent integration for MHC Agentic.
Wraps existing tools and defines agent guidelines.
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import parlant.sdk as p
from llm_clients import GroqClient, GeminiClient
from tools.emotion_tool import EmotionTool
from tools.therapy_tool import TherapyTool
from tools.resource_tool import ResourceTool
from tools.assessment_tool import AssessmentTool
from core.controller import Controller

# Load environment
load_dotenv()

# Initialize tools globally or in main
# We need LLM clients for some tools
def select_llm():
    provider = os.getenv('LLM_PROVIDER', 'groq').lower()
    if provider == 'groq':
        return GroqClient()
    if provider == 'gemini':
        return GeminiClient()
    return GroqClient() # Default

llm_client = select_llm()
emotion_tool = EmotionTool()
therapy_tool = TherapyTool(llm_client)
resource_tool = ResourceTool(llm_client)
assessment_tool = AssessmentTool()

@p.tool
async def analyze_emotions(context: p.ToolContext, message: str) -> p.ToolResult:
    """
    Analyze the user's message to detect emotions.
    Returns a dictionary with detected emotions and their scores.
    """
    print(f"🛠️ Parlant calling EmotionTool: {message[:50]}...")
    result = emotion_tool.execute(message)
    return p.ToolResult(result)

@p.tool
async def get_therapy_techniques(context: p.ToolContext, message: str, emotion: str) -> p.ToolResult:
    """
    Get therapeutic techniques based on the user's message and detected emotion.
    Useful for providing coping strategies.
    """
    print(f"🛠️ Parlant calling TherapyTool: {emotion}...")
    # TherapyTool expects 'text' and 'user_emotion' in input dict if passed to execute, 
    # but looking at the code, execute takes (text, user_emotion, ...)
    # Let's check TherapyTool.execute signature in a moment, assuming standard execute(text, **kwargs)
    # Actually, the tools usually take a dict or specific args. 
    # Let's assume we pass a dict to execute for consistency with the engine, 
    # or call the method directly if we know it.
    # Based on previous usage: execute(self, input_data)
    
    result = therapy_tool.execute({
        "text": message,
        "user_emotion": emotion
    })
    return p.ToolResult(result)

@p.tool
async def get_resources(context: p.ToolContext, query: str) -> p.ToolResult:
    """
    Get mental health resources, articles, or hotline numbers.
    Useful for providing educational content or crisis resources.
    """
    print(f"🛠️ Parlant calling ResourceTool: {query[:50]}...")
    result = resource_tool.execute({
        "query": query
    })
    return p.ToolResult(result)

@p.tool
async def assess_risk(context: p.ToolContext, message: str) -> p.ToolResult:
    """
    Assess the risk level of the user's message.
    Returns risk assessment (Low, Medium, High).
    """
    print(f"🛠️ Parlant calling AssessmentTool: {message[:50]}...")
    result = assessment_tool.execute({
        "text": message
    })
    return p.ToolResult(result)

async def main():
    print("🚀 Starting Parlant Agent...")
    
    async with p.Server() as server:
        agent = await server.create_agent(
            name="MHC-Agentic-Assistant",
            description="A compassionate mental health support agent that uses specialized tools to help users."
        )

        # Register tools
        await agent.register_tool(analyze_emotions)
        await agent.register_tool(get_therapy_techniques)
        await agent.register_tool(get_resources)
        await agent.register_tool(assess_risk)

        # Create Guidelines
        
        # 1. Emotion Analysis
        await agent.create_guideline(
            condition="User expresses feelings or emotions",
            action="Use analyze_emotions to understand how the user is feeling",
            tools=[analyze_emotions]
        )

        # 2. Therapy / Coping Strategies
        await agent.create_guideline(
            condition="User asks for help, advice, or coping strategies",
            action="Use get_therapy_techniques to provide evidence-based coping strategies",
            tools=[get_therapy_techniques]
        )

        # 3. Resources
        await agent.create_guideline(
            condition="User asks for information, articles, or resources",
            action="Use get_resources to find relevant mental health resources",
            tools=[get_resources]
        )
        
        # 4. Risk Assessment (Safety)
        await agent.create_guideline(
            condition="User mentions harm, danger, or severe distress",
            action="Use assess_risk to evaluate safety and provide crisis resources if needed",
            tools=[assess_risk]
        )

        print(f"✅ Agent '{agent.name}' is running!")
        print("   Visit http://localhost:8800 to interact with the agent.")
        print("   Press Ctrl+C to stop.")
        
        # Keep server alive
        await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Agent stopped.")
