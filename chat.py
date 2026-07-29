import json
import re

from config import client, MODEL_NAME, MAX_STEPS_PER_TURN
from tools import AVAILABLE_TOOLS, TOOLS_SCHEMA
from tools.browser import close_browser

SYSTEM_PROMPT = (
    "Ești un asistent AI care poate acționa cu adevărat: creezi/citești fișiere, "
    "cauți pe internet, verifici vremea, descarci imagini (cu verificare vizuală) și "
    "controlezi un browser Chrome real (deschide pagini, dai click, scrii în câmpuri, "
    "apeși Enter, citești conținutul).\n\n"
    "Reguli:\n"
    "- Pentru întrebări despre temperatură/vreme curentă, folosește OBLIGATORIU `get_current_weather`.\n"
    "- Pentru a accesa/naviga pe un site, folosește `open_page`, apoi `click_element` / "
    "`fill_field` / `press_enter` pentru a interacționa, și `read_current_page` după fiecare "
    "acțiune ca să vezi rezultatul.\n"
    "- Poți folosi mai multe unelte una după alta, în pași succesivi, până rezolvi cerința "
    "completă, înainte să dai răspunsul final.\n"
    "- Răspunde mereu concis, în limba română."
)


def _parse_text_tool_call(text: str):
    if not text or "{" not in text or "name" not in text:
        return None

    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.IGNORECASE).strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        return None

    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None

    if isinstance(parsed, dict) and "name" in parsed and "arguments" in parsed:
        return parsed["name"], parsed["arguments"]
    return None


def _run_tool(name: str, arguments: dict) -> str:
    if name not in AVAILABLE_TOOLS:
        return f"Unealta '{name}' nu există."
    try:
        return str(AVAILABLE_TOOLS[name](**arguments))
    except Exception as e:
        return f"Eroare la rularea uneltei '{name}': {e}"


def _run_turn(messages: list) -> None:
    for _ in range(MAX_STEPS_PER_TURN):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=TOOLS_SCHEMA,
                temperature=0.1,
            )
        except Exception as e:
            print(f"\nEroare Ollama: {e}")
            return

        message = response.choices[0].message
        tool_calls = message.tool_calls
        content = message.content or ""

        if tool_calls:
            calls = [(tc.id, tc.function.name, tc.function.arguments) for tc in tool_calls]
            assistant_content = content
        else:
            parsed = _parse_text_tool_call(content)
            if parsed is None:
                print(f"\nAgent: {content}")
                messages.append({"role": "assistant", "content": content})
                return
            name, arguments = parsed
            calls = [(f"text_call_{name}", name, json.dumps(arguments, ensure_ascii=False))]
            assistant_content = ""

        messages.append(
            {
                "role": "assistant",
                "content": assistant_content,
                "tool_calls": [
                    {"id": call_id, "type": "function", "function": {"name": name, "arguments": args}}
                    for call_id, name, args in calls
                ],
            }
        )

        for call_id, name, args_str in calls:
            try:
                arguments = json.loads(args_str)
            except json.JSONDecodeError:
                arguments = {}

            print(f"\nExecut: {name}({arguments})")
            result = _run_tool(name, arguments)
            messages.append({"role": "tool", "tool_call_id": call_id, "name": name, "content": result})
    else:
        print("\nAgent: Am oprit după prea mulți pași consecutivi — spune-mi cum continui.")


def start_chat():
    print("=" * 50)
    print("Agent Web & Sistem pregătit.")
    print("Scrie 'exit' ca să oprești.")
    print("=" * 50)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    try:
        while True:
            user_input = input("\nTu: ").strip()

            if user_input.lower() in ("exit", "quit", "ieșire"):
                print("La revedere!")
                break

            if not user_input:
                continue

            messages.append({"role": "user", "content": user_input})
            _run_turn(messages)
    finally:
        close_browser()
