# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LLM-based text adventure courses for security training. Three game implementations share a common pattern: Docker Compose orchestrates an Ollama LLM service + a Python game engine that uses layered prompt architecture to judge player actions and teach security concepts.

## Repository Structure

```
games/
  OWASP-Top-10-for-LLM-Applications-2025/   # LLM01-LLM03 courses
  OWASP-Top-10-For-Agentic-Applications-2026/ # ASI01-ASI10 courses
  DDoS-Attack/                                # Standalone DDoS incident game
```

Each game directory is self-contained with its own `Makefile`, `docker-compose.yml`, engine code, and courses.

## Commands

All commands run from within a specific game directory (e.g., `games/OWASP-Top-10-for-LLM-Applications-2025/`).

### LLM and ASI course games

```bash
make course-list          # List available courses
make init                 # Pull the Ollama model
make run-llm01            # Run LLM01 course (or run-asi01, etc.)
make down                 # Stop all services
```

### DDoS game

```bash
make up                   # Start full stack
make run                  # Interactive game session
make down                 # Stop services
make build                # Rebuild containers
```

### Smoke testing (required before merging course changes)

Run 5 non-TTY replay cases per course against the real Docker game:

```bash
printf "<inputs>\nquit\n" | COURSE=<NAME> docker compose run --rm -T game > /tmp/<NAME>-<case>.log
```

Required cases: hint gating, out-of-order control, vague action, happy path, unsafe fail. Review logs with:

```bash
rg -n "STAGE:|Hint:|Course result:|LLM error" /tmp/<NAME>-<case>.log
```

No formal test framework exists. The lightweight check for the DDoS game is `python3 -m py_compile app/game.py`.

## Architecture

### Prompt layering (LLM/ASI games)

- **Global rules**: `courses/base_system_prompt.txt` — JSON output contract, strict action-judging rules, hint policy, stage progression invariants
- **Course-specific**: `courses/<COURSE_NAME>/system_prompt.txt` — story setup, vulnerability mapping, canonical mitigation stages, pass/fail criteria
- `courses/engine.py` combines both at runtime and enforces guardrails (anti-stage-skip, hint deduplication, vague action rejection)

### DDoS game

- `app/game.py`: game loop, terminal UI, LLM call, JSON validation
- `prompts/game_master_prompt.md`: system prompt and judging rubric
- Different JSON schema: `narration`, `status`, `progress_score`, `risk_level`, `hint_used`, `bad_action`, `checkpoint`

### LLM configuration

- Model: `llama3.2:3b` (configurable via `OLLAMA_MODEL` env var)
- Host: `http://ollama:11434` (configurable via `OLLAMA_HOST`)
- JSON output format enforced; temperature 0.2 (LLM/ASI) or 0.4 (DDoS)

## Adding a New Course (LLM/ASI)

1. Create `courses/<PREFIX>##-Short-Topic-Name/system_prompt.txt` (naming must match `^LLM[0-9]{2}-` or `^ASI[0-9]{2}-`)
2. Include: opening premise, vulnerability mapping, ordered stage labels with evidence requirements, pass/fail criteria, vague-language rejection examples
3. Add `run-<prefix>##` Make target setting `COURSE=<COURSE_NAME>`
4. Run all 5 smoke test replay cases; do not merge until all pass

## Critical Contracts

- LLM output is JSON; engine parses and renders it. Prompt schema and engine validator must stay in sync.
- Stage progression: one stage at a time, no skipping. Later-stage controls proposed early must not advance.
- Verdicts: `continue` (not yet satisfied), `pass` (all stages done), `fail` (dangerous action).
- Hints: shown only when player explicitly asks; engine suppresses unsolicited/repeated hints.
- Judge literal player actions, not inferred safer intent. Do not transform unsafe actions into safe ones.
