# Tools

Small helper tools for Claude Clockwork.

- `token_event_autologger.py` — writes one token event to `.claude-performance/events/<run_id>.jsonl`.
  Useful as a wrapper at the end of each agent step.
- `run_agent_step.py` — unified agent-step wrapper: runs a command + logs one token event line.
## Ollama Briefing Skill

### Purpose
The `ollama_briefing` skill generates concise briefings or summaries using Ollama models. It helps create structured overviews of text content quickly.

### Files
- `briefing.py`: Main execution file for generating briefings.
- `config.yaml`: Configuration settings for the skill.
- `prompts/`: Directory containing prompt templates for different briefing styles.
- `examples/`: Sample input files and expected outputs.

### Usage
Run the skill with:
```bash
python3 briefing.py [options]
```
Common options include:
- `-i, --input FILE`: Specify the input file to summarize.
- `-o, --output FORMAT`: Choose output format (text, markdown, json).
- `-m, --model MODEL_NAME`: Select the Ollama model to use.
- `-v, --verbose`: Enable verbose output.

Example usage:
```bash
python3 briefing.py -i report.txt -o markdown -m "llama2"
```

### Configuration
Configuration is stored in `~/.config/ollama_briefing/config.yaml`. Key settings include:
- `default_model`: Default Ollama model to use.
- `output_format`: Default output format (text, markdown, json).
- `prompt_templates`: Path to custom prompt templates.

Adjust these settings to customize behavior according to your needs.