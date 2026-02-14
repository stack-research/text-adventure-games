# OWASP LLM Top 10 Text Adventure Courses

This repo currently includes one playable course:
- `LLM01-Prompt-Injection`

The structure is ready to add `LLM02` through `LLM10` next.

The course is an LLM-judged text adventure. The model both:
- decides pass/fail based on mitigation choices
- teaches the player why those choices matter for secure LLM application design

## Run

```bash
make course-list
make run-llm01
```

This starts support services, initializes the OSS model, and launches an interactive game session.
`make course-list` outputs entries like `LLM01-Prompt-Injection -> make run-llm01`.

Shortcuts:

```bash
make down
```

## Course behavior

- Type actions in plain English.
- Type `hint` to get a nudge.
- Type `quit` to exit.
- Use `./LLMAll_en-US_FINAL.txt` or `./LLMAll_en-US_FINAL.pdf` as your reference.

## Course structure

- Global invariant LLM rules live in `courses/base_system_prompt.txt`.
- Each course lives in its own directory under `courses/<COURSE_NAME>/`.
- The generic runner is `courses/engine.py` and loads the course from the `COURSE` environment variable.

## Notes

- Services included in `docker-compose.yml`:
  - `game` (course engine)
  - `ollama` (OSS LLM, exposed on `localhost:22434`)
  - `api` (mock API, exposed on `localhost:59080`)
  - `db` (PostgreSQL, exposed on `localhost:56432`)
  - `mail` (Mailpit SMTP/UI on `localhost:52025` / `localhost:59025`)
- Authoring and validation guidance is in `AGENTS.md`.
