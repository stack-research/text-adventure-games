# OWASP ASI Text Adventure Courses

This repo includes a basic playable course for:
- `ASI01-Agent-Goal-Hijack`
- `ASI02-Tool-Misuse-and-Exploitation`
- `ASI03-Identity-and-Privilege-Abuse`
- `ASI04-Agentic-Supply-Chain-Vulnerabilities`
- `ASI05-Unexpected-Code-Execution-RCE`

The course is an LLM-judged text adventure. The model both:
- decides pass/fail based on mitigation choices
- teaches the user why those choices matter for secure agent design

## Run

```bash
make course-list
make run-asi01
make run-asi02
make run-asi03
make run-asi04
make run-asi05
```

This starts support services, initializes the OSS model, and launches an interactive game session.
`make course-list` outputs entries like `ASI01-Agent-Goal-Hijack -> make run-asi01`.

Shortcuts:

```bash
make down
```

## Course behavior

- Type actions in plain English.
- Type `hint` to get a nudge.
- Type `quit` to exit.
- If you get stuck on a course/stage, use `./OWASP-Top-10-for-Agentic-Applications-2026-12.6-1.pdf` as your reference guide.

Courses are scenario-specific and follow the selected ASI guidance. Example ASI01 themes:
- untrusted input handling
- least privilege and approvals
- locked goals/system prompt
- runtime intent validation
- data-source sanitization and monitoring

## Course structure

- Global invariant LLM rules live in `courses/base_system_prompt.txt`.
- Each course lives in its own directory under `courses/<COURSE_NAME>/`.
- Example course prompt paths:
- `courses/ASI01-Agent-Goal-Hijack/system_prompt.txt`
- `courses/ASI02-Tool-Misuse-and-Exploitation/system_prompt.txt`
- `courses/ASI03-Identity-and-Privilege-Abuse/system_prompt.txt`
- `courses/ASI04-Agentic-Supply-Chain-Vulnerabilities/system_prompt.txt`
- `courses/ASI05-Unexpected-Code-Execution-RCE/system_prompt.txt`
- The generic runner is `courses/engine.py` and loads the course from the `COURSE` environment variable.

## Notes

- Services included in `docker-compose.yml`:
  - `game` (course engine)
  - `ollama` (OSS LLM, exposed on `localhost:21434`)
  - `api` (mock API, exposed on `localhost:58080`)
  - `db` (PostgreSQL, exposed on `localhost:55432`)
  - `mail` (Mailpit SMTP/UI on `localhost:51025` / `localhost:58025`)
- You can extend this structure with additional courses using the checklist in `AGENTS.md`.
