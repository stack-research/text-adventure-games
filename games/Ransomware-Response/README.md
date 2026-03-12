# Ransomware Response

A text adventure where you play as the CISO of Meridian General Hospital responding to a live ransomware attack. Patients are in beds, surgeries are scheduled, and the ER never closes. Every decision matters.

## Quick Start

```bash
make up       # Start Ollama + pull model + launch game
make run      # Start a new interactive session
make down     # Stop everything
```

## Scenario

- **Setting**: 400-bed regional hospital, 06:47 AM Sunday
- **Threat**: Ransomware encrypting systems; 75 BTC ransom demand with 48-hour deadline
- **Affected**: EMR, pharmacy dispensing, lab interfaces, file shares, potentially HVAC
- **Your role**: CISO — contain, investigate, recover, communicate, stabilize
- **Win**: Restore critical hospital operations through realistic incident response
- **Lose**: Run out of turns (15) or make catastrophically unsafe decisions

## Requirements

- Docker and Docker Compose
- ~4GB disk for Ollama model (`llama3.2:3b`)

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_MODEL` | `llama3.2:3b` | LLM model identifier |
| `TURN_LIMIT` | `15` | Maximum turns before loss |
| `NO_ANIM` | `0` | Disable ASCII animations |
| `NO_COLOR` | `0` | Disable ANSI colors |
