# Agent Guide: DDoS-Attack

This file is for future coding agents contributing to this project.

## Project purpose

Build and maintain an LLM-driven terminal text adventure where the player mitigates a live DDoS incident.

Core requirements already implemented:
- OSS LLM in Docker (`ollama` + `llama3.2:3b`)
- Turn-based natural language gameplay
- Strict LLM judging contract via JSON
- Hint/help support without full solution leakage
- Max turn limit loss condition
- Animated terminal ASCII dashboard

## Repository layout

- `app/game.py`: Main game loop, terminal UI, LLM call, response validation
- `app/Dockerfile`: Runtime image for game CLI
- `app/requirements.txt`: Python dependencies
- `prompts/game_master_prompt.md`: System prompt and judging rubric
- `docker-compose.yml`: Orchestrates Ollama, model pull, and game container
- `Makefile`: Operator shortcuts (`make up`, `make run`, etc.)
- `README.md`: User-facing setup/run docs

## Local workflow

Preferred commands:
- `make help`
- `make up` (full stack)
- `make run` (interactive game session)
- `make down`

Lightweight checks before finishing changes:
- `python3 -m py_compile app/game.py`
- `docker compose config`

## Critical contracts (do not break)

1. LLM output schema contract
- `game.py` expects JSON with keys:
  - `narration`, `status`, `progress_score`, `risk_level`, `hint_used`, `bad_action`, `checkpoint`
- `status` must remain one of: `ongoing | won | lost`
- `risk_level` must remain one of: `low | medium | high | critical`

2. Prompt-driven logic
- Keep scenario/rubric in `prompts/game_master_prompt.md`
- Avoid moving gameplay decisions into hardcoded decision trees

3. Turn-limit semantics
- Hint/help requests count as turns
- Reaching the turn limit while still `ongoing` must produce loss

4. UX expectations
- Maintain terminal graphics/dashboard behavior
- Keep `--no-anim` / `NO_ANIM` and `--no-color` / `NO_COLOR` support functional

## Coding guidance

- Keep dependencies minimal and explicit.
- Prefer small pure functions in `game.py` for UI/rendering changes.
- Preserve graceful failures for model/prompt connectivity issues.
- Keep prompts and code aligned if schema/rules change.

## Common pitfalls

- Breaking JSON parsing by changing Ollama response handling.
- Updating prompt schema without updating validator in `game.py`.
- Accidentally disabling interactive TTY behavior in compose config.
- Adding heavy animations that hurt basic terminal compatibility.

## If you change behavior

Update all of:
- `README.md` (user docs)
- `AGENTS.md` (agent docs)
- `prompts/game_master_prompt.md` (if judging/story logic changed)

## Nice-to-have future improvements

- Add automated tests with mocked Ollama responses.
- Add a replay/log mode for incident transcripts.
- Add difficulty presets (turn limits, stricter judging temperature/options).
