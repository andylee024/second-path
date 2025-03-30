# Tech Spec – Strategic Roundtable Advisor (Multi-Agent Terminal)

## 🧠 Purpose
Build a terminal-based multi-agent advisory system where a small group of AI advisors simulate a roundtable discussion about a user’s career direction. Each advisor has a unique worldview and focuses on one of three modes: introspection, research, or analysis. A facilitator agent consolidates the coaches’ outputs into a cohesive, usable summary for the user.

This roundtable replaces the single-agent model with an orchestrated, multi-perspective conversation aimed at better clarity and insight.

---

## 🧱 Tech Stack
- **Language:** Python 3.11+
- **LLM Interface:** OpenAI Assistants API (for memory + session persistence)
- **Data Format:** JSON for memo context and agent responses
- **UI:** Terminal-based CLI
- **Session Management:** One thread per conversation managed via Assistants API

---

## 🎯 Feature Scope – Strategic Roundtable

### Flow Overview
1. Load a hardcoded user memo
2. User selects a mode: `introspection` or `analysis`
3. Initialize one thread using OpenAI Assistants API
4. Each coach agent (e.g. Dalio, Weaver, Naval) responds independently based on selected mode:
   - **Introspection**: Ask powerful questions to uncover more context and insight, and explain why those questions matter
   - **Analysis**: Provide a structured assessment or recommendation in response to a user query (e.g. “What should I do next?”)
5. Facilitator agent:
   - Synthesizes coach responses
   - Identifies themes, tensions, and suggested next steps
   - Outputs a message to the user
6. (Optional) User sees or hides agent reasoning

---

## 🧩 Core Components

### 1. **User Input**
- Loaded from `data/memo.txt`
- Contains career goals, uncertainties, history
- May evolve with user-provided Q&A

```txt
Andy is a YC founder and ex-Uber ATG engineer. He wants to become a founder of a VC-backed AI company solving real-world problems. He is unsure whether to start something solo or join someone, and he's exploring traction opportunities through agents, logistics, and deep technical work.
```

---

### 2. **Coach Agents**
Each agent is initialized with:
- A system prompt with worldview/persona
- A defined `mode`: introspection | analysis
- Access to memo and Q&A thread

**Mode Definitions:**
- **Introspection**: Generate 2–3 powerful questions tailored to the memo + user input, with reasoning behind each question
- **Analysis**: Provide structured recommendations or prioritization based on user-supplied prompt or current situation

**Example output format (Introspection):**
```json
{
  "agent": "Ray Dalio",
  "mode": "introspection",
  "output": [
    "What fear are you avoiding in this transition?",
    "What would your future self say about your current indecision?"
  ],
  "reasoning": "The memo shows a desire for speed, but avoidance of failure. I'm trying to surface this tension."
}
```

**Example output format (Analysis):**
```json
{
  "agent": "Graham Weaver",
  "mode": "analysis",
  "output": "Focus on embedding in a compounding environment before starting something solo. Try apprenticeship or consulting in high-signal orgs.",
  "reasoning": "Based on your memo, you gain momentum from structured intensity. A lightweight embed would let you test paths before overcommitting."
}
```

---

### 3. **Facilitator Agent**
- Receives all agent outputs + reasoning
- Summarizes:
  - Key themes across advisors
  - Contradictions or diverse viewpoints
  - Suggested reflection or next action

**Example output:**
```
"Your advisors are surfacing a core tradeoff between learning fast through action (Naval) and avoiding risk by embedding deeply (Weaver). Dalio wants you to clarify what pain you’re avoiding."

"Suggested reflection: What do you stand to learn fastest by doing the hard thing you’re avoiding most?"
```

---

### 4. **Reasoning Store**
- Every coach’s `reasoning` field is logged
- Can be toggled visible/hidden in the terminal
- Future feature: allow inspection or debugging

---

## 📁 Directory Structure
```bash
src/
├── agent/
│   ├── dalio.py
│   ├── weaver.py
│   ├── naval.py
│   └── facilitator.py
├── prompts/
│   └── coach_system_prompts.py
├── data/
│   └── memo.json
├── roundtable.py           # Runs full session
├── cli.py                  # Terminal entry point
└── utils.py                # Thread helpers, formatting
```

---

## ✅ MVP Checklist
- [ ] Load memo from JSON
- [ ] User selects mode: introspection or analysis
- [ ] Set up 3 coach agents with Assistants API
- [ ] Each agent produces structured output + reasoning
- [ ] Facilitator aggregates and summarizes
- [ ] Terminal view with optional reasoning toggle

---

## 🧠 Notes
- Start with one round of agent output for each mode
- User should feel like they’re sitting in a high-trust, high-clarity strategic conversation
- Once proven, extend to follow-up Q&A and experiment design

---

Once this roundtable works, we can expand to:
- More modes (e.g., experimentation design, future simulation)
- Dynamic coach follow-ups based on user answers
- Structured reflections tied to strategy planning
- UI layer and longitudinal memory tracking
