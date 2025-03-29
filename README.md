# 2nd Path - Strategic Council

A terminal-based agent engine that simulates a Strategic Council. Each agent (Dalio, Naval, Weaver) reads your career memo and generates a strategy proposal. You can then review and select strategies via CLI.

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your OpenAI API key:
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

## Usage

1. Edit `data/memo.json` with your career information
2. Run the CLI:
   ```bash
   python src/cli.py
   ```
3. Review each advisor's strategy and accept/reject as needed
4. Get your composite strategy in `data/composite_strategy.json`

## Project Structure

- `src/agents/`: Individual advisor agents
- `src/prompts/`: System prompts for agents
- `data/`: User memo and generated strategies
- `src/engine.py`: Core engine to coordinate agents
- `src/cli.py`: Command-line interface
