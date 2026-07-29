import re

from playwright.sync_api import sync_playwright

_playwright = None
_browser = None
_page = None


def _get_page():
    global _playwright, _browser, _page
    if _page is None or _page.is_closed():
        if _playwright is None:
            _playwright = sync_playwright().start()
        try:
            _browser = _playwright.chromium.launch(channel="chrome", headless=False)
        except Exception:
            _browser = _playwright.chromium.launch(headless=False)
        _page = _browser.new_page()
    return _page


def close_browser():
    global _playwright, _browser, _page
    try:
        if _browser:
            _browser.close()
        if _playwright:
            _playwright.stop()
    except Exception:
        pass
    finally:
        _playwright = _browser = _page = None


def open_page(url: str) -> str:
    try:
        if not re.match(r"^https?://", url):
            url = "https://" + url

        print(f"\nDeschid pagina: {url}")

        page = _get_page()
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(500)

        return (
            f"Am deschis '{page.title()}' ({page.url}).\n"
            f"Conținut vizibil:\n{page.inner_text('body')[:2000]}"
        )
    except Exception as e:
        return f"Eroare la deschiderea paginii: {e}"


def click_element(target: str) -> str:
    try:
        print(f"\nClick: '{target}'")

        page = _get_page()
        try:
            page.click(target, timeout=4000)
        except Exception:
            page.get_by_text(target, exact=False).first.click(timeout=4000)

        page.wait_for_timeout(500)
        return f"Am dat click pe '{target}'. URL curent: {page.url}"
    except Exception as e:
        return f"Eroare la click pe '{target}': {e}"


def fill_field(selector: str, text: str) -> str:
    try:
        print(f"\nScriu '{text}' în '{selector}'")
        _get_page().fill(selector, text, timeout=4000)
        return f"Am scris '{text}' în câmpul '{selector}'."
    except Exception as e:
        return f"Eroare la scriere în '{selector}': {e}"


def press_enter(selector: str = "") -> str:
    try:
        page = _get_page()
        if selector:
            page.press(selector, "Enter", timeout=4000)
        else:
            page.keyboard.press("Enter")
        page.wait_for_timeout(500)
        return f"Am apăsat Enter. URL curent: {page.url}"
    except Exception as e:
        return f"Eroare la apăsarea Enter: {e}"


def read_current_page() -> str:
    try:
        return _get_page().inner_text("body")[:2500]
    except Exception as e:
        return f"Eroare la citirea paginii: {e}"


def take_screenshot(filename: str = "screenshot.png") -> str:
    try:
        _get_page().screenshot(path=filename)
        return f"Screenshot salvat: {filename}"
    except Exception as e:
        return f"Eroare la screenshot: {e}"


BROWSER_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "open_page",
            "description": (
                "Deschide o pagină web într-un browser Chrome real (vizibil pe ecran) "
                "și întoarce conținutul text vizibil. Folosește asta ca prim pas când "
                "trebuie să accesezi/navighezi pe un site anume."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Adresa paginii, ex: https://exemplu.com"}
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "click_element",
            "description": (
                "Dă click pe un element din pagina curent deschisă în browser. "
                "`target` poate fi un selector CSS (ex: '#login-btn', 'button.submit') "
                "sau textul vizibil al elementului (ex: 'Submit', 'Login')."
            ),
            "parameters": {
                "type": "object",
                "properties": {"target": {"type": "string"}},
                "required": ["target"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fill_field",
            "description": "Scrie text într-un câmp (input/textarea) din pagina curentă, identificat printr-un selector CSS.",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "Selector CSS al câmpului, ex: 'input[name=username]'",
                    },
                    "text": {"type": "string"},
                },
                "required": ["selector", "text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "press_enter",
            "description": "Apasă tasta Enter, opțional într-un câmp specific (selector CSS).",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "Selector CSS opțional al câmpului activ"}
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_current_page",
            "description": "Citește textul vizibil al paginii curent deschise în browser, fără să navigheze.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Salvează o captură de ecran a paginii curente pe disc, ca fișier PNG local.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Numele fișierului PNG, ex: pagina.png"}
                },
                "required": [],
            },
        },
    },
]
