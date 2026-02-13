# Agent Guide: Architecture and Course Authoring

This project hosts OWASP ASI security training as LLM-judged text-adventure courses.

## 1) System Architecture

- Runtime stack is defined at repo root in `docker-compose.yml`.
- Root contains shared runtime orchestration only (services, infra wiring, entrypoints).
- Course content is isolated under `courses/`.

Core components:
- `game` service: runs `courses/engine.py` (generic course runner).
- `ollama` + `ollama-init`: OSS LLM service + model initialization.
- Support services: `db`, `api`, `mail` for realistic multi-service environments.

## 2) Prompt Architecture (Global + Course)

Prompting is intentionally layered:

- Global invariant rules: `courses/base_system_prompt.txt`
  - JSON output contract
  - strict action-judging rules
  - hint policy
  - narrative/education style rules
  - progression behavior
- Course-specific rules: `courses/<COURSE_NAME>/system_prompt.txt`
  - story setup and opening narrative
  - vulnerability mapping to OWASP source content
  - canonical mitigation path
  - pass/fail criteria for that course

`courses/engine.py` combines both at runtime.

## 3) Course Directory Convention

- Each course lives in: `courses/<COURSE_NAME>/`
- Naming format: `ASI##-Short-Topic-Name`
- Example: `courses/ASI01-Agent-Goal-Hijack/`
- Required file per course: `system_prompt.txt`

Only valid course directories should match `^ASI[0-9]{2}-`.

## 4) Execution Model

Use `make` targets (preferred UX):

- `make course-list`:
  - lists valid course names and corresponding run target
- `make run-asi01`:
  - starts support services
  - initializes model
  - launches the ASI01 interactive run
- `make down`:
  - stops the stack

When adding a new course, also add its run target to `Makefile` (e.g., `run-asi02`).

## 5) Engine Behavior Requirements

The LLM must always do both:
- judge game outcome (`continue`, `pass`, `fail`)
- educate the user on why choices are secure/insecure

Non-negotiable evaluation rules:
- Judge literal user action, not inferred safer intent.
- Do not transform unsafe actions into safe ones.
- Do not advance stage unless the action truly satisfies that mitigation step.
- Return `fail` immediately on clearly dangerous or negligent actions defined by course criteria.

Output format is JSON from model, rendered by engine into simple text blocks.

## 6) How To Add a New Course

1. Choose an ASI entry and map source content.
- Use `OWASP-Top-10-for-Agentic-Applications-2026-12.6-1.txt`.
- Extract from:
  - `Description`
  - `Common Examples of the Vulnerability`
  - `Example Attack Scenarios`
  - `Prevention and Mitigation Guidelines`

2. Create course directory.
- `mkdir -p courses/ASI##-Short-Topic-Name`

3. Add `system_prompt.txt`.
- Include:
  - course topic
  - opening simulation premise for `__START__`
  - selected example + attack scenario
  - canonical mitigation stages
  - pass criteria
  - fail criteria

4. Add Make target.
- Add `run-asi##` target in `Makefile` that sets `COURSE=<COURSE_NAME>` and runs game.

5. Verify listing behavior.
- Ensure folder name matches `^ASI[0-9]{2}-` so `make course-list` includes it.

6. Run and test.
- Validate:
  - happy path to `pass`
  - explicit unsafe action path to `fail`
  - vague/non-mitigating action remains `continue`
  - hint requests provide nudges but no full solution

7. Update documentation.
- If needed, update `README.md` course examples and shortcuts.

## 7) Review Checklist for Any New Course

- Source traceability: content maps to OWASP ASI source text.
- Scenario coherence: threat, attack, and mitigations align logically.
- Branch correctness: pass/fail/continue behavior is robust.
- Teaching quality: each response explains security rationale.
- Hint safety: hints nudge, never solve fully.
- Runtime readiness: compose + make workflow runs without manual patching.

## 8) Guardrails for Future Changes

- Keep invariant behavior in `courses/base_system_prompt.txt`.
- Keep variable scenario content in per-course `system_prompt.txt` only.
- Do not introduce per-course code forks unless strictly necessary.
- Prefer extending via new course directories + Make targets.
- Preserve concise stage output formatting in engine (`STAGE: ...`, then spaced sections).
