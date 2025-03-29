# Tech Spec – Strategic Council (Agent Engine CLI)

## 🧠 Purpose
Build a terminal-based agent engine that simulates a Strategic Council. Each agent (e.g. Dalio, Naval, Weaver) reads a user's hard-coded memo and generates a strategy proposal. The user can then review and select strategies via CLI.

---

## 🧱 Tech Stack
- **Language:** Python 3.11+
- **Prompting/LLM:** OpenAI (GPT-4 API)
- **Data Format:** JSON for memos and strategies
- **CLI UI:** Simple print/input prompts
- **Directory Style:** Inspired by ai-hedgefund layout

---

## 📁 Directory Structure
```bash
src/
├── agents/                # Individual advisor agents
│   ├── base.py            # BaseAgent class (shared logic)
│   ├── dalio.py
│   ├── naval.py
│   └── weaver.py
├── prompts/
│   └── system_prompts.py  # Prompt templates for agents
├── data/
│   └── memo.json          # Hardcoded user career memo
├── engine.py              # Core engine to call agents
├── cli.py                 # Command-line interface logic
├── strategy.py            # Data models for strategy objects
└── utils.py               # Helpers (e.g., formatting)
```

---

## 🧩 Components

### 1. `data/memo.json`
A static JSON file with the user's memo (name, context, ambitions, uncertainties).
```json
{
  "name": "Andy",
  "background": "YC founder, ex-Uber ATG engineer",
  "goal": "Become a founder of a VC-backed AI company solving real-world problems",
  "uncertainties": ["Start solo or join?", "What opportunities exist?"],
  "energy_signals": ["AI agents", "Physical world problems"]
}
```

### 2. `BaseAgent` (base.py)
Abstract class with shared logic for calling GPT API with memo context + strategy template.
```python
class BaseAgent:
    def __init__(self, name: str, style: str, system_prompt: str):
        self.name = name
        self.style = style
        self.system_prompt = system_prompt

    def generate_strategy(self, memo: dict) -> dict:
        # Call OpenAI API with system prompt + memo
        # Return structured dictionary with outcome, fit, plan, experiments, uncertainties
        ...
```

### 3. `agent_name.py`
Each advisor imports `BaseAgent` and defines their system prompt.
```python
class NavalAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Naval",
            style="Leverage & Asymmetric Bets",
            system_prompt=system_prompts.NAVAL
        )
```

### 4. `prompts/system_prompts.py`
Stores advisor voice + strategy generation instructions.
```python
NAVAL = "You are Naval Ravikant. Read this user's memo and suggest a strategy..."
```

### 5. `engine.py`
Main controller that loads memo, initializes agents, and fetches strategies.
```python
from agents.naval import NavalAgent
from agents.dalio import DalioAgent
...

AGENTS = [NavalAgent(), DalioAgent(), WeaverAgent()]

def generate_all_strategies(memo):
    return {agent.name: agent.generate_strategy(memo) for agent in AGENTS}
```

### 6. `cli.py`
CLI interface that allows the user to:
- View the memo
- View each strategy proposal
- Accept/reject each one
- Output a final composite strategy

```python
print("Welcome to 2nd Path – Strategic Council")
print("Your Memo Summary: ...")

for agent_name, strategy in strategies.items():
    print(f"\n{agent_name} Strategy:")
    print(json.dumps(strategy, indent=2))
    response = input("Accept this strategy? (y/n/tweak): ")
```

### 7. `strategy.py`
Defines the format for a strategy object.
```python
class Strategy:
    advisor: str
    outcome: str
    rationale: str
    plan: str
    experiments: list[str]
    uncertainties: list[str]
```

---

## ✅ MVP Goals
- [ ] Hardcoded memo input (JSON)
- [ ] 3 advisor agents with unique strategy outputs
- [ ] CLI to view and accept/reject strategies
- [ ] Combine accepted strategies into a single composite
