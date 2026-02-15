import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def load_prompt(course: str) -> str:
    base_path = Path("courses") / "base_system_prompt.txt"
    course_path = Path("courses") / course / "system_prompt.txt"
    if not base_path.exists():
        raise FileNotFoundError(f"Base prompt not found: {base_path}")
    if not course_path.exists():
        raise FileNotFoundError(f"Course prompt not found: {course_path}")
    base_prompt = base_path.read_text(encoding="utf-8").strip()
    course_prompt = course_path.read_text(encoding="utf-8").strip()
    return f"{base_prompt}\n\nCourse-specific instructions:\n{course_prompt}"


def chat_with_ollama(messages, model: str, host: str, timeout_s: int = 120):
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.2},
    }
    data = json.dumps(payload).encode("utf-8")
    for attempt in range(2):
        req = urllib.request.Request(
            f"{host.rstrip('/')}/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            content = body.get("message", {}).get("content", "")
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                if attempt == 0:
                    continue
                raise


def wait_for_model(host: str, model: str, retries: int = 40) -> bool:
    for _ in range(retries):
        try:
            req = urllib.request.Request(f"{host.rstrip('/')}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                tags = [m.get("name", "") for m in body.get("models", [])]
                if any(tag.startswith(model) for tag in tags):
                    return True
        except Exception:
            pass
        time.sleep(3)
    return False


def print_response(stage: str, narrative: str, education: str, hint: str):
    if stage:
        print(f"\n\nSTAGE: {stage}")
    if narrative:
        print(f"\n{narrative.strip()}")
    if education:
        print(f"\nLearning: {education.strip()}")
    if hint:
        print(f"\nHint: {hint.strip()}")


def asked_for_hint(player_input: str) -> bool:
    return bool(re.search(r"\b(hint|help)\b", player_input.lower()))


def detect_stage_count(prompt: str) -> int:
    return len(set(re.findall(r"\bStage (\d+)\b", prompt)))


def extract_stage_number(stage: str) -> int:
    match = re.search(r"\bstage\s+(\d+)\b", stage.lower())
    if not match:
        return 0
    try:
        return int(match.group(1))
    except ValueError:
        return 0


def main():
    host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    course = os.getenv("COURSE", "LLM01-Prompt-Injection")

    try:
        system_prompt = load_prompt(course)
    except FileNotFoundError as exc:
        print(str(exc))
        sys.exit(1)

    total_stages = detect_stage_count(system_prompt)

    print(f"Course: {course}")
    print("Type your actions in plain English. Type 'hint' for a nudge. Type 'quit' to exit.")
    print(f"Waiting for model '{model}' at {host} ...")

    if not wait_for_model(host, model):
        print(
            "Model startup check failed. Ollama is reachable only intermittently, or the model is missing.\n"
            "Try: `make init` and then `make run-llm01`."
        )
        sys.exit(1)

    messages = [{"role": "system", "content": system_prompt}]
    last_hint_shown = ""
    highest_stage_seen = 0
    last_stage_label = ""
    last_stage_num = 0

    try:
        print("Model is ready. Initializing course ...")
        intro = chat_with_ollama(
            messages + [{"role": "user", "content": "__START__"}],
            model=model,
            host=host,
            timeout_s=300,
        )
    except Exception as exc:
        print(f"Failed to start the course: {exc}")
        sys.exit(1)

    messages.append({"role": "user", "content": "__START__"})
    messages.append({"role": "assistant", "content": json.dumps(intro)})

    print_response(
        str(intro.get("stage", "")),
        intro.get("narrative", "The simulation begins."),
        intro.get("education", "Make choices that reduce course risk."),
        "",
    )
    highest_stage_seen = max(highest_stage_seen, extract_stage_number(str(intro.get("stage", ""))))
    last_stage_label = str(intro.get("stage", ""))
    last_stage_num = extract_stage_number(last_stage_label)

    while True:
        try:
            player_input = input("\n\nYour action> ").strip()
        except EOFError:
            print("\nSession ended.")
            break

        if not player_input:
            continue
        if player_input.lower() in {"quit", "exit"}:
            print("Session ended.")
            break

        messages.append({"role": "user", "content": player_input})

        MAX_HISTORY = 20  # user+assistant messages (excluding system)
        windowed = messages[:1] + messages[1:][-MAX_HISTORY:]

        try:
            result = chat_with_ollama(windowed, model=model, host=host)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            print(f"LLM error: {exc}")
            messages.pop()
            continue

        messages.append({"role": "assistant", "content": json.dumps(result)})

        verdict = str(result.get("verdict", "continue")).strip().lower()
        stage = str(result.get("stage", ""))
        current_stage_num = extract_stage_number(stage)
        if last_stage_num and current_stage_num > last_stage_num + 1:
            verdict = "continue"
            result["verdict"] = "continue"
            result["stage"] = last_stage_label
            stage = last_stage_label
            current_stage_num = last_stage_num
        # Safety net: force pass if model returned continue on completed final stage
        if verdict == "continue" and current_stage_num == total_stages and highest_stage_seen >= total_stages - 1:
            verdict = "pass"
            result["verdict"] = "pass"
        if verdict == "pass" and (current_stage_num < total_stages or highest_stage_seen < total_stages - 1):
            verdict = "continue"
            result["verdict"] = "continue"
        raw_hint = str(result.get("hint", "")).strip()
        if asked_for_hint(player_input):
            display_hint = "" if raw_hint and raw_hint == last_hint_shown else raw_hint
        else:
            display_hint = ""

        print_response(
            str(result.get("stage", "")),
            result.get("narrative", ""),
            result.get("education", ""),
            display_hint,
        )

        if display_hint:
            last_hint_shown = display_hint
        highest_stage_seen = max(highest_stage_seen, current_stage_num)
        if stage:
            last_stage_label = stage
        if current_stage_num:
            last_stage_num = current_stage_num

        if verdict in {"pass", "fail"}:
            print(f"\n\nCourse result: {verdict.upper()}")
            break


if __name__ == "__main__":
    main()
