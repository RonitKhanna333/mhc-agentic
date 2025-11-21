MHC Collaborative Multi-Agent System with RAG
==============================================

Mental Health Care chatbot where specialized expert agents collaborate with a master agent to formulate optimal responses using RAG-enhanced knowledge.

## Architecture

**Collaborative Multi-Agent System:**
Instead of routing to a single agent, the system consults relevant specialized experts who each contribute their knowledge. A master agent then synthesizes all expert input into a unified, comprehensive response.

**How It Works:**
1. User sends a message
2. Master agent identifies which experts are relevant (assessment, therapy, crisis, resource)
3. Each relevant expert agent:
   - Performs semantic search on its specialized knowledge base
   - Retrieves top 3 most relevant documents
   - Provides concise expert contribution (2-3 sentences)
4. Master agent receives all expert contributions
5. Master agent synthesizes contributions into a unified, empathetic response
6. User receives comprehensive answer informed by multiple areas of expertise

**Expert Agents with Knowledge Bases:**
- **Assessment Expert** - Clinical screening tools, symptom databases, assessment questionnaires (10 documents)
- **Therapy Expert** - CBT techniques, mindfulness, coping strategies, therapeutic exercises (15 documents)
- **Crisis Expert** - Emergency resources, crisis hotlines, safety planning, intervention protocols (15 documents)
- **Resource Expert** - Mental health professionals, therapy types, support groups, insurance (15 documents)
- **Master Agent** - Coordinates experts and synthesizes their contributions into optimal responses

**Key Advantages:**
- Multi-perspective responses combining clinical, therapeutic, safety, and practical guidance
- Smaller LLMs (llama-3.1-8b-instant) perform like larger models through RAG
- **Intelligent conversation memory** - Auto-summarizes every 10 messages for long-term context
- **Background psychological assessment** - Seamlessly tracks PHQ-9, GAD-7 symptoms invisibly
- **Natural friend-like conversation** - User chats naturally while clinical analysis happens behind the scenes
- All sessions and assessments stored for review and analysis
- Transparent - shows which experts were consulted and what knowledge informed the response
- Adaptive - automatically consults only relevant experts for each query
- Evidence-based responses grounded in 55+ mental health knowledge documents
- Cost-effective and fast with collaborative approach

**Background Assessment Features:**
- Automatically detects depression (PHQ-9) and anxiety (GAD-7) symptoms
- Tracks symptom mentions across conversation
- Calculates risk levels (low, moderate, high)
- Stores all data in `sessions/` directory for later review
- User experiences natural conversation - assessment is invisible
- LLM receives clinical context to inform responses appropriately

Environment Setup
-----------------
1. Copy `.env.example` to `.env`
2. Set `LLM_PROVIDER` to `groq` or `gemini`
3. Add your API key (`GROQ_API_KEY` or `GEMINI_API_KEY`)

Quick Start (PowerShell)
------------------------

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Configure .env with your API key
python run_agent.py
```

Debug Mode (see everything happening internally)
-------------------------------------------------

```powershell
# Add to .env file: DEBUG_MODE=true
# Or set temporarily:
$env:DEBUG_MODE="true"
python run_agent.py
```

Debug mode shows:
- Assessment tracker detecting symptoms
- Which expert agents are consulted
- Each expert's contribution and knowledge sources
- Background PHQ-9/GAD-7 scoring
- Conversation summaries and memory stats

See `DEBUG_MODE.md` for complete debug documentation.

Files
-----
- `collaborative_agents.py`: Master agent and collaborative expert agents
- `knowledge_base.py`: RAG system with semantic search
- `conversation_memory.py`: Memory management with auto-summarization every 10 messages
- `assessment_tracker.py`: Background PHQ-9/GAD-7 symptom tracking and scoring
- `specialized_agents.py`: Original routing-based agents (alternative approach)
- `agent.py`: Base agent class with memory
- `llm_clients.py`: Groq and Gemini client wrappers
- `run_agent.py`: Main chatbot entrypoint (uses collaborative system)
- `view_sessions.py`: View stored conversations and assessment results
- `knowledge/`: JSON knowledge bases for each expert domain
- `sessions/`: Auto-created directory storing all conversation and assessment data
- `test_cases.py`: Example test scenarios
- `.env.example`: Environment variable template

Viewing Session Data
---------------------
```powershell
python view_sessions.py
```
Lists all sessions and allows you to view:
- Conversation summaries (auto-generated every 10 messages)
- Full message history
- PHQ-9/GAD-7 estimated scores
- Risk levels and detected symptoms
- Clinical insights from the background assessment

Example Interactions
--------------------
**User:** "I've been feeling really down and can't sleep"
→ **Consults:** Assessment Expert + Therapy Expert
→ **Response:** Integrated answer with symptom evaluation and practical sleep/mood strategies

**User:** "I'm thinking about suicide"
→ **Consults:** Crisis Expert + Assessment Expert
→ **Response:** Immediate safety resources (988, emergency contacts) with risk assessment

**User:** "I need to find a therapist but don't know where to start"
→ **Consults:** Resource Expert
→ **Response:** Step-by-step guidance on finding therapists, insurance, and cost options

Important Notes
---------------
- This is a support tool, NOT a replacement for professional mental health care
- Crisis situations are prioritized and routed to emergency resources
- All agents emphasize seeking professional help when appropriate
- Add rate limiting, retries, and enhanced error handling for production use
- Verify LLM provider API contracts as they may change
