# Skill Task: screencast_script

Ziel: Screencast-Skripte (Storyboard + Narration) als Markdown erzeugen.

```json
{
  "type": "skill_request_spec",
  "request_id": "req-video-001",
  "skill_id": "screencast_script",
  "inputs": {
    "project_root": ".",
    "path": "Docs/Documentation/Screencast_Quickstart.md",
    "script_spec": {
      "title": "Quickstart Screencast",
      "audience": "End users",
      "goal": "Show installation + first run",
      "duration": "5-7 min",
      "chapters": [
        {"timestamp": "00:00", "title": "Intro", "on_screen": "Open repo", "narration": "What we will do"},
        {"timestamp": "01:00", "title": "Install", "on_screen": "Run install command", "narration": "Explain prerequisites"}
      ],
      "notes": "Keep secrets off-screen. Use a demo environment."
    },
    "overwrite": true
  }
}
```
