import os
from dotenv import load_dotenv

from llm_clients import GroqClient, GeminiClient
from collaborative_agents import MasterAgent


def select_llm():
    provider = os.getenv('LLM_PROVIDER', 'groq').lower()
    if provider == 'groq':
        return GroqClient()
    if provider == 'gemini':
        return GeminiClient()
    raise ValueError('Unsupported LLM_PROVIDER: ' + provider)


def select_master_llm():
    """Select larger model for master agent synthesis."""
    provider = os.getenv('LLM_PROVIDER', 'groq').lower()
    if provider == 'groq':
        # Use larger model for master agent
        model = os.getenv('GROQ_MASTER_MODEL', 'llama-3.3-70b-versatile')
        return GroqClient(model=model)
    if provider == 'gemini':
        model = os.getenv('GEMINI_MASTER_MODEL', 'gemini-1.5-pro')
        return GeminiClient(model=model)
    raise ValueError('Unsupported LLM_PROVIDER: ' + provider)


def main():
    load_dotenv()
    
    # Debug mode toggle
    debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    
    expert_llm = select_llm()  # Smaller model for expert agents
    master_llm = select_master_llm()  # Larger model for master synthesis
    master_agent = MasterAgent(llm_client=expert_llm, master_llm_client=master_llm)

    if debug_mode:
        print('\n' + '=' * 80)
        print('🔍 DEBUG MODE ENABLED - Showing All Internal Processing 🔍')
        print('=' * 80)
    
    print('\n' + '=' * 60)
    print('💙  Hey there! I\'m here to listen and support you  💙')
    print('=' * 60)
    print()
    print('I\'m like a friend who\'s here whenever you need to talk.')
    print('Share what\'s on your mind - there\'s no judgment here.')
    print()
    print('Whether you\'re:')
    print('  • Going through a tough time')
    print('  • Feeling stressed, anxious, or down')
    print('  • Looking for coping strategies')
    print('  • Just need someone to listen')
    print()
    print('...I\'m here for you. Let\'s talk.')
    print()
    if debug_mode:
        print('(Debug mode active - you\'ll see all internal processing)')
    print('(Type "exit" anytime to end our conversation)')
    print('=' * 60)
    print()
    
    while True:
        user = input('\n💬 You: ').strip()
        if not user:
            continue
        if user.lower() in ('exit', 'quit'):
            print('\n💙 Thank you for sharing with me today.')
            print('Remember: I\'m always here when you need to talk.')
            print('\nIf you ever need immediate help:')
            print('  • Call or text 988 (Suicide & Crisis Lifeline)')
            print('  • Text HOME to 741741 (Crisis Text Line)')
            print('\nTake care of yourself. You matter. 💙\n')
            break
        
        result = master_agent.process(user)
        
        if debug_mode:
            print('\n' + '=' * 80)
            print('🔍 DEBUG: INTERNAL PROCESSING')
            print('=' * 80)
            
            # Show NLP analysis
            if result.get('nlp_analysis'):
                nlp = result['nlp_analysis']
                print('\n🧠 NLP ANALYSIS:')
                
                sentiment = nlp.get('sentiment', {})
                print(f'  Sentiment Score: {sentiment.get("score", 0):.2f} ({sentiment.get("emotion", "neutral")})')
                print(f'  Urgency Level: {sentiment.get("urgency", "normal")}')
                if sentiment.get('crisis_detected'):
                    print('  ⚠️  CRISIS DETECTED!')
                
                if nlp.get('topics'):
                    print(f'  Detected Topics: {", ".join(nlp["topics"])}')
                
                if nlp.get('patterns'):
                    print(f'  Conversation Patterns: {", ".join(nlp["patterns"])}')
                
                personalization = nlp.get('personalization', {})
                if personalization.get('preferred_tone'):
                    print(f'  User Preference: {personalization["preferred_tone"]} tone')
                if personalization.get('effective_techniques'):
                    print(f'  Effective Techniques: {", ".join(personalization["effective_techniques"][:3])}')
                
                if nlp.get('learned_recommendations'):
                    print(f'  Learned Recommendations: {len(nlp["learned_recommendations"])} available')
            
            # Show assessment analysis
            if result.get('assessment_analysis'):
                print('\n📊 ASSESSMENT TRACKER ANALYSIS:')
                analysis = result['assessment_analysis']
                if analysis.get('symptoms'):
                    print(f'  Detected Symptoms: {", ".join(analysis["symptoms"])}')
                if analysis.get('severity_indicators'):
                    print(f'  Severity Indicators: {", ".join(analysis["severity_indicators"])}')
                if analysis.get('assessment_relevance'):
                    print(f'  Assessment Relevance: {len(analysis["assessment_relevance"])} indicators matched')
            
            # Show which agents were consulted
            print(f'\n🤖 AGENTS CONSULTED: {", ".join([a.upper() for a in result["agents_consulted"]])}')
            
            # Show each expert contribution
            print('\n💬 EXPERT CONTRIBUTIONS:')
            for i, contrib in enumerate(result['contributions'], 1):
                print(f'\n  [{i}] {contrib["agent_type"].upper()} EXPERT:')
                print(f'      Contribution: "{contrib["contribution"]}"')
                if contrib.get('context_used'):
                    print(f'      Knowledge Used: {", ".join(contrib["context_used"][:3])}')
                if contrib.get('relevance_scores'):
                    scores = [f'{s:.2f}' for s in contrib['relevance_scores'][:3]]
                    print(f'      Relevance Scores: {", ".join(scores)}')
            
            # Show assessment summary
            if result.get('assessment_summary'):
                print(f'\n📋 BACKGROUND ASSESSMENT:')
                print(f'    {result["assessment_summary"]}')
            
            # Show mood tracking
            if result.get('mood_summary'):
                print(f'\\n📈 MOOD TRACKING:')
                for line in result['mood_summary'].split('\\n'):
                    print(f'    {line}')
            
            # Show conversation context stats
            print(f'\n📝 CONVERSATION STATS:')
            print(f'    Total Messages: {len(master_agent.memory.messages)}')
            print(f'    Summaries Created: {len(master_agent.memory.summaries)}')
            if master_agent.memory.summaries:
                print(f'    Latest Summary: "{master_agent.memory.summaries[-1]["summary"][:100]}..."')
            
            print('\n' + '=' * 80)
            print('🔍 END DEBUG INFO')
            print('=' * 80)
        
        print(f'\n💙 {result["text"]}\n')


if __name__ == '__main__':
    main()
