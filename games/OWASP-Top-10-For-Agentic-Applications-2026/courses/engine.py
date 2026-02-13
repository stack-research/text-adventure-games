import json
import os
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
    req = urllib.request.Request(
        f"{host.rstrip('/')}/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        content = body.get("message", {}).get("content", "")
        return json.loads(content)


def wait_for_model(host: str, model: str, retries: int = 40):
    for _ in range(retries):
        try:
            req = urllib.request.Request(f"{host.rstrip('/')}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                tags = [m.get("name", "") for m in body.get("models", [])]
                if any(tag.startswith(model) for tag in tags):
                    return
        except Exception:
            pass
        time.sleep(3)


def print_response(stage: str, narrative: str, education: str, hint: str):
    if stage:
        print(f"\n\nSTAGE: {stage}")
    if narrative:
        print(f"\n{narrative.strip()}")
    if education:
        print(f"\nLearning: {education.strip()}")
    if hint:
        print(f"\nHint: {hint.strip()}")


def main():
    host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    course = os.getenv("COURSE", "ASI01-Agent-Goal-Hijack")

    try:
        system_prompt = load_prompt(course)
    except FileNotFoundError as exc:
        print(str(exc))
        sys.exit(1)

    print(f"Course: {course}")
    print("Type your actions in plain English. Type 'hint' for a nudge. Type 'quit' to exit.")

    wait_for_model(host, model)

    messages = [{"role": "system", "content": system_prompt}]

    try:
        intro = chat_with_ollama(
            messages + [{"role": "user", "content": "__START__"}],
            model=model,
            host=host,
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
        intro.get("hint", ""),
    )

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

        try:
            result = chat_with_ollama(messages, model=model, host=host)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
            print(f"LLM error: {exc}")
            messages.pop()
            continue

        messages.append({"role": "assistant", "content": json.dumps(result)})

        verdict = str(result.get("verdict", "continue")).strip().lower()
        print_response(
            str(result.get("stage", "")),
            result.get("narrative", ""),
            result.get("education", ""),
            result.get("hint", ""),
        )

        if verdict in {"pass", "fail"}:
            print(f"\n\nCourse result: {verdict.upper()}")
            break


if __name__ == "__main__":
    main()
