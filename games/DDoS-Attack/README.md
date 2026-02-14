# DDoS Attack Text Adventure (LLM-Driven)

This project is an interactive text adventure where you play as an on-call network admin mitigating a live DDoS attack.

The game logic is judged by an OSS LLM running in Docker (Ollama + `llama3.2:3b`), not a hardcoded command tree.

## What is implemented

- Natural language turn-by-turn gameplay
- LLM receives:
  - Full story context
  - Canonical success path
  - Strict judging criteria
- Structured judging output (JSON schema) each turn
- Hint/help handling without full solution disclosure
- Max turn limit (default `12`), where reaching the limit means attackers win
- Hint/help requests count as a turn
- Animated terminal ASCII graphics:
  - Boot splash pulse animation
  - Live incident dashboard
  - ASCII network map + telemetry bars

## Files

- `docker-compose.yml`: Runs Ollama, pulls OSS model, and runs the game container
- `app/game.py`: CLI game engine and LLM interaction
- `app/Dockerfile`: Game container build
- `prompts/game_master_prompt.md`: System prompt with story, success path, and judging rules

## Run with Docker Compose

```bash
docker compose up --build
```

Note: Ollama host port is published dynamically to avoid conflicts with other Docker projects.
To see the current mapped port:

```bash
docker compose port ollama 11434
```

When services are ready, attach to the `game` container prompt in the compose output and start playing.

To run game container only after setup:

```bash
docker compose run --rm game
```

## Makefile shortcuts

```bash
make up
make run
```

Other helpful targets:
- `make build`
- `make down`
- `make logs`
- `make ps`
- `make clean`

## Local run (optional)

If you already have Ollama running locally:

```bash
cd app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PROMPT_FILE=../prompts/game_master_prompt.md OLLAMA_HOST=http://localhost:11434 python game.py
```

## Gameplay notes

- Enter one mitigation action per turn in plain language.
- Aim for actions shaped like: `<check data>` or `<apply mitigation>` + `<target system>`.
- Ask for `hint` or `help` if needed (counts as a turn).
- Win by stabilizing service through realistic layered mitigation.
- Lose if turn limit is reached or catastrophic actions cause failure.

Example turn inputs:
- `Check NetFlow and CDN logs to classify L3/L4 versus L7 traffic.`
- `Enable WAF challenge mode for /login and /api/auth with conservative rate limits.`
- `Request ISP FlowSpec for top abusive source prefixes hitting R1.`
- `Validate success in Grafana using 503 rate, p95 latency, and successful sessions.`

## Terminal UI options

- Disable animations:
  - CLI: `python game.py --no-anim`
  - Env: `NO_ANIM=1`
- Disable ANSI colors:
  - CLI: `python game.py --no-color`
  - Env: `NO_COLOR=1`
