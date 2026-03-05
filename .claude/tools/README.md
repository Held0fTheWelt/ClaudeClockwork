# Tools

Small helper tools for Claude Clockwork.

- `token_event_autologger.py` — writes one token event to `.claude-performance/events/<run_id>.jsonl`.
  Useful as a wrapper at the end of each agent step.
- `run_agent_step.py` — unified agent-step wrapper: runs a command + logs one token event line.
