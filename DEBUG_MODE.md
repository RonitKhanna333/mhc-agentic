# Debug Mode Guide

## Enabling Debug Mode

Add to your `.env` file:
```
DEBUG_MODE=true
```

Or set temporarily in terminal:
```powershell
$env:DEBUG_MODE="true"
python run_agent.py
```

## What Debug Mode Shows

### 1. Assessment Tracker Analysis
For EVERY user message, shows:
- **Detected Symptoms**: Keywords matched (depression, anxiety, sleep, etc.)
- **Severity Indicators**: High frequency words (very, extremely, always)
- **Assessment Relevance**: How many PHQ-9/GAD-7 indicators were triggered

Example:
```
📊 ASSESSMENT TRACKER ANALYSIS:
  Detected Symptoms: depression, sleep, energy
  Severity Indicators: persistent, high_frequency
  Assessment Relevance: 3 indicators matched
```

### 2. Agent Routing
Shows which expert agents were consulted:
```
🤖 AGENTS CONSULTED: ASSESSMENT, THERAPY
```

### 3. Expert Contributions
Shows EACH expert's contribution with details:
```
💬 EXPERT CONTRIBUTIONS:

  [1] ASSESSMENT EXPERT:
      Contribution: "Based on persistent low mood and sleep issues, 
                     screening for depression severity using PHQ-9 framework recommended"
      Knowledge Used: Depression Symptoms Overview, PHQ-9 Assessment Tool
      Relevance Scores: 0.85, 0.72, 0.68

  [2] THERAPY EXPERT:
      Contribution: "Sleep hygiene and behavioral activation techniques 
                     can help with both sleep and mood"
      Knowledge Used: Sleep Hygiene Principles, Behavioral Activation for Depression
      Relevance Scores: 0.91, 0.78
```

### 4. Background Assessment Summary
Clinical picture being tracked invisibly:
```
📋 BACKGROUND ASSESSMENT:
    Risk Level: MODERATE | Symptoms discussed: depression, sleep, energy | 
    Key concerns: Significant depression symptoms; 3 different symptom areas identified
```

### 5. Conversation Statistics
Memory and summarization stats:
```
📝 CONVERSATION STATS:
    Total Messages: 12
    Summaries Created: 1
    Latest Summary: "User reports persistent low mood, sleep difficulties, 
                     and low energy for past 2 weeks. Discussed sleep hygiene..."
```

## Understanding the Flow

### Normal User View (DEBUG_MODE=false)
```
💬 You: I've been feeling really down lately and can't sleep

💙 I hear you - that sounds really tough. When you're not sleeping well 
   and feeling down, everything feels harder. Have you noticed if anything 
   specific is keeping you awake at night?
```

### Debug View (DEBUG_MODE=true)
```
💬 You: I've been feeling really down lately and can't sleep

===============================================================================
🔍 DEBUG: INTERNAL PROCESSING
===============================================================================

📊 ASSESSMENT TRACKER ANALYSIS:
  Detected Symptoms: depression, sleep
  Severity Indicators: persistent
  Assessment Relevance: 2 indicators matched

🤖 AGENTS CONSULTED: ASSESSMENT, THERAPY

💬 EXPERT CONTRIBUTIONS:

  [1] ASSESSMENT EXPERT:
      Contribution: "Low mood with sleep disturbance suggests possible 
                     depression - assess duration and severity"
      Knowledge Used: Depression Symptoms Overview, PHQ-9 Assessment Tool
      Relevance Scores: 0.87, 0.73

  [2] THERAPY EXPERT:
      Contribution: "Sleep hygiene basics and mood tracking can help 
                     establish patterns"
      Knowledge Used: Sleep Hygiene Principles, Behavioral Activation
      Relevance Scores: 0.82, 0.69

📋 BACKGROUND ASSESSMENT:
    Risk Level: LOW-MODERATE | Symptoms discussed: depression, sleep

📝 CONVERSATION STATS:
    Total Messages: 2
    Summaries Created: 0
    Latest Summary: (none yet - summaries created every 10 messages)

===============================================================================
🔍 END DEBUG INFO
===============================================================================

💙 I hear you - that sounds really tough. When you're not sleeping well 
   and feeling down, everything feels harder. Have you noticed if anything 
   specific is keeping you awake at night?
```

## What Gets Tracked in Background

### PHQ-9 (Depression) Symptoms Detected:
1. Little interest/pleasure → keywords: interest, pleasure, enjoy
2. Feeling down/depressed → keywords: sad, down, depressed, hopeless
3. Sleep problems → keywords: sleep, insomnia, tired
4. Low energy → keywords: energy, tired, exhausted, fatigue
5. Appetite changes → keywords: appetite, eating, food, weight
6. Feeling bad about self → keywords: worthless, failure, guilt
7. Concentration → keywords: focus, concentrate, attention
8. Psychomotor changes → keywords: restless, slow, fidgety
9. Suicidal thoughts → keywords: suicide, kill myself, harm myself

### GAD-7 (Anxiety) Symptoms Detected:
1. Feeling nervous/anxious → keywords: anxious, nervous, worried
2. Can't control worry → keywords: worry, control, stop
3. Worrying too much → keywords: worry, too much
4. Trouble relaxing → keywords: relax, tense, calm
5. Restlessness → keywords: restless, sit still
6. Irritability → keywords: irritable, angry, annoyed
7. Feeling afraid → keywords: afraid, scared, fear

### Scoring Logic:
- Each symptom mention adds to estimated score
- Frequency/severity words multiply the score
- Risk levels: Low (0-9), Moderate (10-14), High (15+)
- Suicidal keywords → automatic HIGH risk flag

## Using Debug Mode

**For Development:**
- See what knowledge bases are being accessed
- Verify expert agents are being called correctly
- Check if symptoms are being detected
- Monitor conversation summarization

**For Testing:**
- Verify PHQ-9/GAD-7 tracking is working
- Test different symptom combinations
- Check risk level calculations
- Ensure knowledge retrieval is relevant

**For Demonstrations:**
- Show the sophisticated multi-agent system in action
- Prove background assessment is happening
- Display RAG knowledge retrieval
- Illustrate conversation memory management

## Tips

1. **Start with DEBUG_MODE=true** to understand the system
2. **Switch to DEBUG_MODE=false** for natural user experience
3. **Check `sessions/` folder** for stored data even without debug mode
4. **Use `view_sessions.py`** to analyze conversations after they happen
5. **Combine with session viewer** for complete picture of what was tracked
