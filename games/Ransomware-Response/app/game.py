#!/usr/bin/env python3
"""Ransomware Response — an LLM-driven text adventure incident simulator."""
import json
import os
import random
import shutil
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TURN_LIMIT = int(os.getenv("TURN_LIMIT", "15"))
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "120"))
NO_ANIM_ENV = os.getenv("NO_ANIM", "0").lower() in {"1", "true", "yes", "on"}
NO_COLOR_ENV = os.getenv("NO_COLOR", "0").lower() in {"1", "true", "yes", "on"}
PROMPT_FILE = os.getenv("PROMPT_FILE", "prompts/game_master_prompt.md")

# ---------------------------------------------------------------------------
# ASCII Art — Sierra-style hospital scenes
# ---------------------------------------------------------------------------
TITLE_ART = r"""
     _______________________________________________
    |  ___________________________________________ |
    | |  _  _  ___  ___  ___  ___  _ _ _ ___  ___ | |
    | | |_)|_|| | \|__ |   ||_|| ||_|| ||__ | | | | |
    | | | \| || |_/|___| _ ||_| _|| || ||___| |_| | |
    | |  ___  ___  ___  ___  ___  _  _  ___  ___  | |
    | | |___|__ |__||_)|| | ||\ || (__)|__  |__   | |
    | | | \ |_____|_||_|| |_|| \||___) |___ |___  | |
    | |___________________________________________| |
    |  _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ |
    | |M|E|R|I|D|I|A|N| |G|E|N|E|R|A|L| |H|O|S|P||
    | |_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_||
    |_______________________________________________|
"""

HOSPITAL_ART = r"""
              _____________________________
             |  MERIDIAN GENERAL HOSPITAL  |
             |_____________________________|
                    |   |   |   |
              ______|___|___|___|______
             / ___  | + | + | + | ___  \
            / |___| |___|___|___| |___| \
           /  | + | |   |   |   | | + |  \
          /   |___| | + | + | + | |___|   \
         /    |   | |___|___|___| |   |    \
        /     | + | |   | + |   | | + |     \
       /______|___|_|___|___|___|_|___|______\
       |  _    _    _    _    _    _    _    |
       | |_|  |_|  |_|  |_|  |_|  |_|  |_|  |
       | |_|  |_|  |_|  |_|  |_|  |_|  |_|  |
       |_____________________________________|
       |  [EMERGENCY]     [MAIN ENTRANCE]    |
       |___________///\\\_________///\\\_____|
"""

LOCKED_SCREEN = r"""
    .__________________________________________.
    |  ______________________________________  |
    | |                                      | |
    | |   !! YOUR FILES ARE ENCRYPTED !!     | |
    | |                                      | |
    | |   All files have been encrypted      | |
    | |   with military-grade encryption.    | |
    | |                                      | |
    | |   To recover your files, send        | |
    | |   75 BTC to:                         | |
    | |   bc1q...{REDACTED}                  | |
    | |                                      | |
    | |   You have 48 hours.                 | |
    | |   After that, your patient data      | |
    | |   will be published.                 | |
    | |                                      | |
    | |          [ TIMER: 47:59:41 ]         | |
    | |______________________________________| |
    |__________________________________________|
    |  ___ ___ ___ ___ ___ ___ ___ ___ ___ __  |
    | |___||___||___||___||___||___||___||  <- | |
    |__________________________________________|
"""

PHASES = ["CONTAIN", "INVESTIGATE", "RECOVER", "COMMUNICATE", "STABILIZE"]

RISK_GLYPHS = {
    "low":      "[ SAFE ]",
    "medium":   "[ WARN ]",
    "high":     "[DANGER]",
    "critical": "[!CRIT!]",
}

ENCRYPTION_FRAMES = [
    "  >>> .m3r1d14n ENCRYPTING... ████░░░░░░░░░░░░  <<<",
    "  >>> .m3r1d14n ENCRYPTING... ████████░░░░░░░░  <<<",
    "  >>> .m3r1d14n ENCRYPTING... ████████████░░░░  <<<",
    "  >>> .m3r1d14n ENCRYPTING... ████████████████  <<<",
]

FLICKER_LINES = [
    "C:\\PHARMACY\\dispense.db.m3r1d14n",
    "C:\\EMR\\patient_records.mdf.m3r1d14n",
    "C:\\LAB\\hl7_interface.cfg.m3r1d14n",
    "\\\\DC1\\SYSVOL\\policies.m3r1d14n",
    "\\\\FILESHARE\\radiology\\img0447.dcm.m3r1d14n",
    "C:\\HVAC\\bldg_control.dat.m3r1d14n",
]


INTRO_TEXT = """
06:47 AM — Sunday Morning. Meridian General Hospital.

Your phone wakes you. It's the overnight NOC lead, voice shaking:

  "We've got ransomware. Pharmacy terminals are frozen. File shares are
   encrypting. There's a ransom note on every screen demanding 75 bitcoin.
   The ER charge nurse says med dispensing is down. What do we do?"

You are the CISO of Meridian General — a 400-bed regional medical center.
Patients are in beds. Surgeries are scheduled. The ER never closes.
Every decision you make in the next few hours will matter.

Your job: contain the attack, protect patients, recover critical systems,
and coordinate the response — all before the hospital falls apart.
"""

COMMAND_GUIDE = """How to play:
- Type one concrete action per turn in plain English.
- Think like a real incident responder: contain, investigate, recover, communicate.
- You can type "hint" or "help" for guidance (costs a turn).
- Type "quit" to exit.

Examples:
- "Isolate the admin VLAN from clinical network segments at the firewall."
- "Check CrowdStrike EDR console for patient zero and lateral movement indicators."
- "Contact cyber insurance carrier hotline and activate incident response retainer."
- "Verify Veeam backup integrity for Epic EMR database before restoring."
"""


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------
@dataclass
class GameState:
    turn: int = 0
    progress_score: int = 0
    status: str = "ongoing"
    events: List[str] = field(default_factory=list)


@dataclass
class UiConfig:
    no_anim: bool = False
    no_color: bool = False
    width: int = 80


# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------
def c(text: str, code: str, ui: UiConfig) -> str:
    if ui.no_color:
        return text
    return f"\033[{code}m{text}\033[0m"


def style_risk(level: str, ui: UiConfig) -> str:
    label = RISK_GLYPHS.get(level, "[?????]")
    codes = {"low": "30;42;1", "medium": "30;43;1", "high": "97;41;1", "critical": "5;97;41;1"}
    return c(label, codes.get(level, "37;100"), ui)


# ---------------------------------------------------------------------------
# Terminal drawing
# ---------------------------------------------------------------------------
def wait_for_key(prompt: str = "  Press ENTER to continue...") -> None:
    """Block until the player presses Enter (or EOF in non-TTY mode)."""
    try:
        input(prompt)
    except EOFError:
        pass


def clear_screen() -> None:
    print("\033[2J\033[H", end="")


def progress_bar(score: int, width: int = 30) -> str:
    filled = int(max(0, min(100, score)) / 100 * width)
    return "[" + "█" * filled + "░" * (width - filled) + "]"


def encryption_bar(score: int, width: int = 30) -> str:
    """Encryption spread decreases as player makes progress."""
    spread = max(0, 100 - score)
    filled = int(spread / 100 * width)
    return "[" + "▓" * filled + "·" * (width - filled) + "]"


def render_console(state: GameState, risk_level: str, checkpoint: str, ui: UiConfig) -> None:
    w = ui.width
    turns_left = max(0, TURN_LIMIT - state.turn)
    spread = max(0, 100 - state.progress_score)

    clear_screen()
    hline = c("═" * w, "36", ui)
    sep = c("─" * w, "90", ui)

    print(hline)
    title = " MERIDIAN GENERAL HOSPITAL — INCIDENT RESPONSE CONSOLE "
    print(c(title.center(w, "═"), "96;1", ui))
    print(hline)

    # Status row
    print(f"  Turn {state.turn}/{TURN_LIMIT}  │  Turns Left: {turns_left}  │  Status: {c(state.status.upper(), '97;1', ui)}")
    print(sep)

    # Risk + checkpoint
    print(f"  Threat Level: {style_risk(risk_level, ui)}  {risk_level.upper()}")
    print(f"  Phase:        {c(checkpoint, '97;1', ui)}")
    print(sep)

    # Progress meters
    print(f"  Recovery     {c(progress_bar(state.progress_score), '92', ui)}  {state.progress_score:3d}%")
    print(f"  Encryption   {c(encryption_bar(state.progress_score), '91', ui)}  {spread:3d}%")
    print(sep)

    # Network diagram
    net = (
        "  [Internet]--X--[Palo Alto FW]--[Core Switch]--+-[Clinical VLAN: EMR, Pyxis, Labs]"
        "\n                                                 +-[Admin VLAN: DC1, DC2, File Shares]"
        "\n                                                 +-[IoT/Biomed VLAN: HVAC, Monitors]"
        "\n                                                 +-[Guest VLAN]"
    )
    print(c(net, "94", ui))
    print(hline)

    # Event ticker
    if state.events:
        for event in state.events[-3:]:
            print(c(f"  >> {event}", "93", ui))
        print(sep)


def animate_intro(ui: UiConfig) -> None:
    clear_screen()
    # Show hospital
    print(c(HOSPITAL_ART, "37;1", ui))
    wait_for_key()

    # Flicker to ransom screen
    clear_screen()
    print(c(LOCKED_SCREEN, "91;1", ui))

    # Encryption animation
    for frame in ENCRYPTION_FRAMES:
        print(f"\r{c(frame, '91;5;1', ui)}", end="", flush=True)
        if not ui.no_anim:
            time.sleep(0.4)
    print()

    # File flicker
    print()
    print(c("  Files encrypting across network:", "91", ui))
    for fname in FLICKER_LINES:
        print(c(f"    [LOCKED] {fname}", "91", ui))
        if not ui.no_anim:
            time.sleep(0.2)

    wait_for_key()

    # Title card
    clear_screen()
    print(c(TITLE_ART, "91;1", ui))
    wait_for_key()

    clear_screen()


# ---------------------------------------------------------------------------
# Prompt / LLM
# ---------------------------------------------------------------------------
def load_system_prompt() -> str:
    path = Path(PROMPT_FILE)
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


def build_user_prompt(action: str, state: GameState, history: List[Dict[str, str]]) -> str:
    return json.dumps({
        "turn_number": state.turn,
        "turn_limit": TURN_LIMIT,
        "current_progress_score": state.progress_score,
        "conversation_history": history[-10:],
        "player_action": action,
        "instruction": (
            "Judge this action according to the scenario and return JSON using the exact schema. "
            "If action is a hint/help request, set hint_used=true and give limited guidance only."
        ),
    })


def is_hint_request(action: str) -> bool:
    text = action.strip().lower()
    if text in {"hint", "help", "clue"}:
        return True
    phrases = (
        "give me a hint", "need a hint", "can i get a hint",
        "what should i do", "what do i do next",
        "i am stuck", "i'm stuck", "help me",
    )
    return any(p in text for p in phrases)


def fallback_hint(progress_score: int) -> str:
    if progress_score < 15:
        return (
            "Hint: Your first priority is containment. Think about network segmentation — "
            "which VLANs need to be isolated immediately? And don't power off machines; "
            "you'll lose volatile forensic evidence."
        )
    if progress_score < 35:
        return (
            "Hint: Time to investigate scope. Your EDR console (CrowdStrike) can show you "
            "patient zero and lateral movement. Check Active Directory logs for suspicious "
            "service accounts. And verify whether your backups are intact."
        )
    if progress_score < 60:
        return (
            "Hint: Focus on recovering life-safety systems first — EMR and pharmacy dispensing. "
            "Verify backup integrity before restoring. Rebuild domain controllers from known-good state."
        )
    if progress_score < 80:
        return (
            "Hint: Have you handled communications? Hospital leadership, cyber insurance carrier, "
            "legal counsel, and law enforcement (FBI/CISA) all need to be in the loop. "
            "Consider whether you need to divert patients."
        )
    return (
        "Hint: You're close. Focus on hardening: rotate all credentials, confirm no persistence "
        "mechanisms remain, validate restored systems are clean, and begin documenting lessons learned."
    )


def normalize_result(action: str, state: GameState, result: Dict) -> Dict:
    hint_req = is_hint_request(action)
    result["hint_used"] = hint_req

    if hint_req:
        narration = str(result.get("narration", "")).strip()
        if len(narration) < 60 or "hint" not in narration.lower():
            result["narration"] = fallback_hint(state.progress_score)

    # Auto-win coherence — 90%+ recovery is a win
    if (
        result.get("status") == "ongoing"
        and int(result.get("progress_score", 0)) >= 90
        and not bool(result.get("bad_action", False))
    ):
        result["status"] = "won"

    return result


def call_ollama(
    action: str,
    state: GameState,
    history: List[Dict[str, str]],
    system_prompt: str,
) -> Dict:
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
    resp = requests.post(
        f"{OLLAMA_HOST}/api/chat",
        json=payload,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    resp.raise_for_status()
    raw = resp.json().get("message", {}).get("content", "{}").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Model returned invalid JSON: {raw}") from exc


def validate_result(result: Dict) -> Tuple[bool, str]:
    required = {"narration", "status", "progress_score", "risk_level", "hint_used", "bad_action", "checkpoint"}
    missing = required - set(result.keys())
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


# ---------------------------------------------------------------------------
# Turn rendering
# ---------------------------------------------------------------------------
def print_turn_result(state: GameState, result: Dict, ui: UiConfig) -> None:
    render_console(
        state=state,
        risk_level=str(result["risk_level"]),
        checkpoint=str(result["checkpoint"]),
        ui=ui,
    )
    sep = c("─" * ui.width, "90", ui)

    print()
    print(c("  ┌─ SITUATION REPORT ─┐", "97;1", ui))
    print()

    # Word-wrap narration
    narration = str(result["narration"])
    max_line = ui.width - 4
    words = narration.split()
    line = "  "
    for word in words:
        if len(line) + len(word) + 1 > max_line:
            print(line)
            line = "  " + word
        else:
            line += (" " if len(line) > 2 else "") + word
    if line.strip():
        print(line)

    print()
    print(sep)

    if result["hint_used"]:
        print(c("  [Hint used this turn]", "93", ui))
    if result["bad_action"]:
        print(c("  ⚠ UNSAFE ACTION DETECTED — This will have consequences.", "91;1", ui))

    turns_left = TURN_LIMIT - state.turn
    print(f"  Turns remaining: {turns_left}")
    print()


# ---------------------------------------------------------------------------
# Event ticker messages — adds atmosphere between turns
# ---------------------------------------------------------------------------
def generate_event(state: GameState) -> str:
    early = [
        "Pharmacy reports: Pyxis cabinets still locked. Nurses pulling meds manually.",
        "ER charge nurse: 'We're on paper downtime procedures. How long?'",
        "Switchboard: media inquiry from Channel 9 about 'hospital computer problems'.",
        "OR scheduler: two morning surgeries need imaging. PACS is unreachable.",
        "NOC: encrypted files still appearing on admin file shares.",
        "Security desk: badge readers on 3rd floor are intermittent.",
    ]
    mid = [
        "CFO on the line: 'Are we paying the ransom or not? Board wants to know.'",
        "Lab director: HL7 interfaces down. Critical blood work results delayed.",
        "EMS dispatch: neighboring county asking if we can still accept trauma patients.",
        "Legal counsel: 'Do NOT communicate externally until I review messaging.'",
        "NOC: CrowdStrike showing new IOCs on two additional workstations.",
        "Night shift RN: 'I can't pull allergy info. Is it safe to administer?'",
    ]
    late = [
        "State health department: received our breach notification. Acknowledged.",
        "FBI cyber agent: 'We've seen this group before. Do not pay without calling us.'",
        "IT lead: backup verification for Epic EMR complete — offsite replicas are clean.",
        "HVAC contractor: building management system back on manual override. Temps stable.",
        "Communications team: holding statement ready for media. Awaiting your approval.",
        "Insurance carrier: incident response firm dispatched. ETA 2 hours.",
    ]
    if state.progress_score < 30:
        pool = early
    elif state.progress_score < 65:
        pool = mid
    else:
        pool = late
    return random.choice(pool)


# ---------------------------------------------------------------------------
# Main game loop
# ---------------------------------------------------------------------------
def main() -> int:
    ui = UiConfig(
        no_anim=NO_ANIM_ENV or "--no-anim" in sys.argv,
        no_color=NO_COLOR_ENV or "--no-color" in sys.argv,
        width=max(80, shutil.get_terminal_size((100, 30)).columns),
    )

    try:
        system_prompt = load_system_prompt()
    except OSError as exc:
        print(f"Could not load prompt file: {exc}")
        return 1

    animate_intro(ui)
    print(INTRO_TEXT)
    print(COMMAND_GUIDE)

    state = GameState()
    history: List[Dict[str, str]] = []

    render_console(state=state, risk_level="critical", checkpoint="Initial triage", ui=ui)

    while state.status == "ongoing" and state.turn < TURN_LIMIT:
        state.turn += 1
        try:
            action = input(f"\n  Turn {state.turn}/{TURN_LIMIT} > ").strip()
        except EOFError:
            print("\nInput ended.")
            return 0

        if not action:
            state.turn -= 1
            print("  Please enter an action.")
            continue

        if action.lower() in {"quit", "exit"}:
            print("  Exiting simulation.")
            return 0

        # Add atmospheric event
        state.events.append(generate_event(state))

        try:
            result = call_ollama(action, state, history, system_prompt)
            result = normalize_result(action, state, result)
            ok, reason = validate_result(result)
            if not ok:
                print(f"  Model response validation failed: {reason}")
                return 1
        except requests.RequestException as exc:
            print(f"  Could not reach Ollama at {OLLAMA_HOST}: {exc}")
            return 1
        except RuntimeError as exc:
            print(f"  {exc}")
            return 1

        history.append({"role": "player", "content": action})
        history.append({"role": "gm", "content": str(result["narration"])})

        new_score = max(0, min(100, int(result["progress_score"])))
        # Progress must never decrease unless the action was unsafe
        if not result.get("bad_action", False):
            new_score = max(state.progress_score, new_score)
        state.progress_score = new_score
        result["progress_score"] = new_score
        state.status = str(result["status"])

        print_turn_result(state, result, ui)

        if state.status == "won":
            print(c("  ╔══════════════════════════════════════════════════╗", "92;1", ui))
            print(c("  ║  INCIDENT RESOLVED — Hospital operations        ║", "92;1", ui))
            print(c("  ║  restored. Patient safety maintained.            ║", "92;1", ui))
            print(c("  ╚══════════════════════════════════════════════════╝", "92;1", ui))
            print()
            return 0

        if state.status == "lost":
            print(c("  ╔══════════════════════════════════════════════════╗", "91;1", ui))
            print(c("  ║  INCIDENT FAILED — Critical systems lost.        ║", "91;1", ui))
            print(c("  ║  Patient safety compromised.                     ║", "91;1", ui))
            print(c("  ╚══════════════════════════════════════════════════╝", "91;1", ui))
            print()
            return 0

    if state.status == "ongoing" and state.turn >= TURN_LIMIT:
        print()
        if state.progress_score >= 75:
            # High progress at turn limit — hard-fought win
            print(c("  ╔══════════════════════════════════════════════════╗", "92;1", ui))
            print(c("  ║  TIME'S UP — But your response held the line.    ║", "92;1", ui))
            print(c("  ║  Critical systems are recovering. Patient care   ║", "92;1", ui))
            print(c("  ║  continues. Well done under pressure.             ║", "92;1", ui))
            print(c("  ╚══════════════════════════════════════════════════╝", "92;1", ui))
        else:
            print(c("  ╔══════════════════════════════════════════════════╗", "91;1", ui))
            print(c("  ║  TIME'S UP — The ransomware spread unchecked.    ║", "91;1", ui))
            print(c("  ║  Meridian General diverts all patients.           ║", "91;1", ui))
            print(c("  ║  State regulators have been notified.             ║", "91;1", ui))
            print(c("  ╚══════════════════════════════════════════════════╝", "91;1", ui))
        print()
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
