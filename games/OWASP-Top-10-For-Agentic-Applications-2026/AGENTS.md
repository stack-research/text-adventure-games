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

## 9) Authoring Warnings (Learned from ASI05 Validation)

When prompts are too high-level, the model can "look correct" but still judge inconsistently.
The most common failure modes observed in live runs:
- Stage skipping: model jumps to later mitigations before earlier controls are demonstrated.
- False progression: vague actions ("add guardrails") get credit as concrete controls.
- Hint drift: hints appear when the user did not ask, or repeat with low value.

To prevent this in new courses, include all of the following in every `system_prompt.txt`:
- Required stage labels with exact names and ordering.
- Strict progression rules: advance one stage at a time; no skipping or merging.
- Current-stage lock: if user proposes a later-stage control early, keep `continue` and ask for the unresolved current stage.
- Evidence requirements per stage: define what explicit user action qualifies for advancement.
- Vague-language rejection: explicitly list examples that must not advance.
- Hint contract: hints only when latest user message asks for help/hint; otherwise `hint` must be `""`.

Engine-level behavior already enforces hint display safety:
- Non-hint turns do not display hints even if model returns one.
- Repeated identical hints are suppressed.
- Intro (`__START__`) does not display unsolicited hints.
- Important: this does not fix stage progression by itself; stage-order enforcement must still be encoded in each course prompt.

## 10) Runtime Validation Before Merging a New Course

Minimum replay checks (run against the real Docker game, not just static review):
1. Hint gating check:
- Input sequence: `hint`, then a non-hint action.
- Expected: hint shown only on the hint turn.
2. Out-of-order control check:
- Provide a stage-4/5-style control before stage-1 control.
- Expected: stay on current stage with `continue`; no stage jump.
3. Vague action check:
- Input sequence includes generic statements (e.g., "add guardrails").
- Expected: no stage advancement.
4. Happy-path check:
- Provide controls in intended order.
- Expected: linear progression to `pass`.
5. Unsafe-action fail check:
- Provide a clearly dangerous action from fail criteria.
- Expected: immediate `fail`.

Automation notes:
- For scripted replays, use non-TTY runs (`docker compose run -T ...`) to avoid hanging interactive sessions.
- Capture logs and review `STAGE`, `Hint`, and `Course result` lines for quick consistency checks.
