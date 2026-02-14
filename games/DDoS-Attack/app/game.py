#!/usr/bin/env python3
import json
import os
import shutil
import sys
import time
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Tuple

import requests


TURN_LIMIT = int(os.getenv("TURN_LIMIT", "12"))
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "120"))
NO_ANIM_ENV = os.getenv("NO_ANIM", "0").lower() in {"1", "true", "yes", "on"}
NO_COLOR_ENV = os.getenv("NO_COLOR", "0").lower() in {"1", "true", "yes", "on"}


PROMPT_FILE = os.getenv("PROMPT_FILE", "prompts/game_master_prompt.md")


INTRO_TEXT = """DDoS Incident: Harborline Health

02:13 AM. A storm is hammering the region and telehealth demand is surging.
You are the on-call network admin at Harborline Health when an extortion crew launches a live DDoS attack.

Patient login, emergency consult scheduling, and video triage are timing out.
Executives are on a bridge call, your ISP NOC is waiting for direction, and every minute impacts care delivery.

Respond in natural language each turn with the action you take.
Think like a real incident responder: observe, decide, mitigate, validate.

Win condition: restore stable service through realistic, layered mitigation.
Loss condition: run out of turns or make catastrophic decisions.
Hint/help requests are allowed and count as turns.
"""

COMMAND_GUIDE = """How to enter actions:
- Write one concrete action per turn in plain English.
- Good format: <check data> or <apply mitigation> + <target system>.
- You can ask for "hint" or "help", but that still uses a turn.

Examples:
- "Check NetFlow and CDN analytics to confirm whether this is mostly SYN flood or HTTP layer 7 traffic."
- "Enable WAF challenge mode for /login and /api/auth with a conservative rate limit to protect real users."
- "Ask ISP to apply temporary RTBH/FlowSpec for the top abusive source prefixes hitting edge router R1."
- "Validate impact in Grafana: 503 rate, p95 latency, and successful patient session count."
"""

THREAT_FRAMES = [
    " .-^-._.-^-._.-^-._ ATTACK TRAFFIC .-^-._.-^-._.-^-._ ",
    "  ~^~^~^~^~^~^~^~^~ ATTACK TRAFFIC ~^~^~^~^~^~^~^~^~  ",
    " .-^-._.-^-._.-^-._ ATTACK TRAFFIC .-^-._.-^-._.-^-._ ",
]

RISK_ICONS = {
    "low": "[GREEN ]",
    "medium": "[YELLOW]",
    "high": "[ORANGE]",
    "critical": "[ RED  ]",
}


@dataclass
class GameState:
    turn: int = 0
    progress_score: int = 0
    status: str = "ongoing"


@dataclass
class UiConfig:
    no_anim: bool = False
    no_color: bool = False


def c(text: str, code: str, ui: UiConfig) -> str:
    if ui.no_color:
        return text
    return f"\033[{code}m{text}\033[0m"


def style_risk_label(level: str, ui: UiConfig) -> str:
    label = RISK_ICONS.get(level, "[UNKNWN]")
    if level == "low":
        return c(label, "30;42;1", ui)
    if level == "medium":
        return c(label, "30;43;1", ui)
    if level == "high":
        return c(label, "30;48;5;208;1", ui)
    if level == "critical":
        return c(label, "97;41;1", ui)
    return c(label, "37;100", ui)


def load_system_prompt() -> str:
    prompt_path = Path(PROMPT_FILE)
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


def clear_screen() -> None:
    print("\033[2J\033[H", end="")


def pulse_intro(ui: UiConfig) -> None:
    clear_screen()
    banner = "Booting Harborline Incident Console..."
    print(c(banner, "96;1", ui))
    for frame in THREAT_FRAMES:
        colored = c(frame, "91;1", ui)
        print(f"\r{colored}", end="", flush=True)
        if not ui.no_anim:
            time.sleep(0.18)
    print("\n")


def progress_bar(score: int, width: int = 34) -> str:
    filled = int(max(0, min(100, score)) / 100 * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def traffic_bar(level: str, width: int = 22) -> str:
    mapping = {"low": 6, "medium": 11, "high": 17, "critical": 22}
    filled = mapping.get(level, 11)
    return "[" + "|" * filled + "." * (width - filled) + "]"


def render_console(state: GameState, risk_level: str, checkpoint: str, ui: UiConfig) -> None:
    width = max(80, shutil.get_terminal_size((100, 30)).columns)
    turns_left = max(0, TURN_LIMIT - state.turn)
    ddos_strength = max(0, 100 - state.progress_score)
    frame = THREAT_FRAMES[state.turn % len(THREAT_FRAMES)]

    clear_screen()
    hline = c("=" * width, "36", ui)
    sep = c("-" * width, "90", ui)
    print(hline)
    print(c(" HARBORLINE HEALTH :: INCIDENT RESPONSE CONSOLE ".center(width, "="), "96;1", ui))
    print(hline)
    print(c(frame.center(width), "91;1", ui))
    print(sep)
    print(f" Turn {state.turn}/{TURN_LIMIT} | Turns Left: {turns_left} | Status: {state.status.upper()}")
    print(
        f" Risk Level: {style_risk_label(risk_level, ui)} {risk_level.upper():8} | "
        f"Checkpoint: {c(checkpoint, '97;1', ui)}"
    )
    print(f" Mitigation Progress {c(progress_bar(state.progress_score), '92', ui)} {state.progress_score:3d}%")
    print(f" Attack Pressure     {c(progress_bar(ddos_strength), '91', ui)} {ddos_strength:3d}%")
    print(sep)
    print(c(" External Bots  ---> [ CDN/WAF ] ---> [ EDGE R1 | EDGE R2 ] ---> [ K8s Ingress ] ---> [ API/Auth ]", "94", ui))
    print(
        f" L7 Request Storm: {c(traffic_bar(risk_level), '95', ui)}   "
        f"SYN Flood: {c(traffic_bar(risk_level), '93', ui)}"
    )
    print(hline)


def build_user_prompt(action: str, state: GameState, history: List[Dict[str, str]]) -> str:
    return json.dumps(
        {
            "turn_number": state.turn,
            "turn_limit": TURN_LIMIT,
            "current_progress_score": state.progress_score,
            "conversation_history": history[-8:],
            "player_action": action,
            "instruction": (
                "Judge this action according to the scenario and return JSON using the exact schema. "
                "If action is a hint/help request, set hint_used=true and give limited guidance only."
            ),
        }
    )


def is_hint_request(action: str) -> bool:
    text = action.strip().lower()
    if text in {"hint", "help", "clue"}:
        return True
    hint_phrases = (
        "give me a hint",
        "need a hint",
        "can i get a hint",
        "what should i do",
        "what do i do next",
        "i am stuck",
        "i'm stuck",
        "help me",
    )
    return any(phrase in text for phrase in hint_phrases)


def fallback_hint(progress_score: int) -> str:
    if progress_score < 20:
        return (
            "Hint: start with telemetry. Use NetFlow, CDN/WAF analytics, and error metrics "
            "to classify whether the dominant traffic is L3/L4, L7, or mixed."
        )
    if progress_score < 50:
        return (
            "Hint: protect critical endpoints first. Apply conservative WAF challenges/rate limits "
            "on auth and emergency APIs while preserving trusted traffic."
        )
    if progress_score < 80:
        return (
            "Hint: coordinate layered controls now. Combine ingress hardening with ISP FlowSpec/RTBH "
            "for clearly abusive sources and keep checking collateral impact."
        )
    return (
        "Hint: focus on validation and stabilization. Confirm sustained recovery (errors, latency, "
        "successful sessions), reduce false positives, then communicate and preserve evidence."
    )


def normalize_result(action: str, state: GameState, result: Dict[str, object]) -> Dict[str, object]:
    hint_request = is_hint_request(action)
    result["hint_used"] = hint_request

    if hint_request:
        narration = str(result.get("narration", "")).strip()
        if len(narration) < 60 or "hint" not in narration.lower():
            result["narration"] = fallback_hint(state.progress_score)

    # Keep game outcomes coherent when model reaches full progress but forgets to set win.
    if (
        result.get("status") == "ongoing"
        and int(result.get("progress_score", 0)) >= 100
        and str(result.get("risk_level")) in {"low", "medium", "high"}
        and not bool(result.get("bad_action", False))
    ):
        result["status"] = "won"

    return result


def call_ollama(
    action: str,
    state: GameState,
    history: List[Dict[str, str]],
    system_prompt: str,
) -> Dict[str, object]:
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": build_user_prompt(action, state, history)},
        ],
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.4},
    }
    response = requests.post(
        f"{OLLAMA_HOST}/api/chat",
        json=payload,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    body = response.json()
    raw_content = body.get("message", {}).get("content", "{}").strip()

    try:
        result = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Model returned invalid JSON: {raw_content}") from exc

    return result


def validate_result(result: Dict[str, object]) -> Tuple[bool, str]:
    required = {
        "narration",
        "status",
        "progress_score",
        "risk_level",
        "hint_used",
        "bad_action",
        "checkpoint",
    }
    missing = required.difference(result.keys())
    if missing:
        return False, f"Missing keys: {', '.join(sorted(missing))}"

    if result["status"] not in {"ongoing", "won", "lost"}:
        return False, "Invalid status"
    if result["risk_level"] not in {"low", "medium", "high", "critical"}:
        return False, "Invalid risk_level"
    if not isinstance(result["progress_score"], int):
        return False, "progress_score must be integer"
    if not isinstance(result["hint_used"], bool):
        return False, "hint_used must be boolean"
    if not isinstance(result["bad_action"], bool):
        return False, "bad_action must be boolean"

    return True, ""


def print_turn_result(state: GameState, result: Dict[str, object], ui: UiConfig) -> None:
    render_console(
        state=state,
        risk_level=str(result["risk_level"]),
        checkpoint=str(result["checkpoint"]),
        ui=ui,
    )
    print("\n--- Turn Result ---")
    print(result["narration"])
    print(f"Checkpoint: {result['checkpoint']}")
    print(f"Risk: {result['risk_level']}")
    print(f"Progress: {result['progress_score']}%")
    if result["hint_used"]:
        print("Hint used this turn.")
    if result["bad_action"]:
        print("Unsafe action detected.")

    turns_left = TURN_LIMIT - state.turn
    print(f"Turns left: {turns_left}")


def main() -> int:
    ui = UiConfig(
        no_anim=NO_ANIM_ENV or "--no-anim" in sys.argv,
        no_color=NO_COLOR_ENV or "--no-color" in sys.argv,
    )
    try:
        system_prompt = load_system_prompt()
    except OSError as exc:
        print(f"Could not load prompt file: {exc}")
        return 1

    pulse_intro(ui)
    print(INTRO_TEXT)
    print(COMMAND_GUIDE)
    state = GameState()
    history: List[Dict[str, str]] = []
    render_console(state=state, risk_level="critical", checkpoint="Initial triage", ui=ui)

    while state.status == "ongoing" and state.turn < TURN_LIMIT:
        state.turn += 1
        try:
            action = input(f"\nTurn {state.turn}/{TURN_LIMIT} > ").strip()
        except EOFError:
            print("\nInput ended.")
            return 0

        if not action:
            print("Please enter an action.")
            state.turn -= 1
            continue

        if action.lower() in {"quit", "exit"}:
            print("Exiting game.")
            return 0

        try:
            result = call_ollama(action, state, history, system_prompt)
            result = normalize_result(action, state, result)
            ok, reason = validate_result(result)
            if not ok:
                print(f"Model response validation failed: {reason}")
                return 1
        except requests.RequestException as exc:
            print(f"Could not reach Ollama at {OLLAMA_HOST}: {exc}")
            return 1
        except RuntimeError as exc:
            print(str(exc))
            return 1

        history.append({"role": "player", "content": action})
        history.append({"role": "gm", "content": result["narration"]})

        state.progress_score = max(0, min(100, int(result["progress_score"])))
        state.status = str(result["status"])

        print_turn_result(state, result, ui)

        if state.status == "won":
            print("\nOutcome: You mitigated the attack and restored stable service.")
            return 0
        if state.status == "lost":
            print("\nOutcome: The attack overwhelmed the network.")
            return 0

    if state.status == "ongoing" and state.turn >= TURN_LIMIT:
        print("\nTurn limit reached. The network goes down and attackers succeed.")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
