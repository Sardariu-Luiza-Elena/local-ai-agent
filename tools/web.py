import html
import re
import urllib.parse
import urllib.request


def search_web(query: str) -> str:
    try:
        print(f"\nCaut pe internet: '{query}'...")

        encoded_query = urllib.parse.quote(query)
        url = f"https://lite.duckduckgo.com/lite/?q={encoded_query}"
        request = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )

        with urllib.request.urlopen(request, timeout=10) as response:
            page = response.read().decode("utf-8")

        text = re.sub(r"<script.*?>.*?</script>", "", page, flags=re.DOTALL)
        text = re.sub(r"<style.*?>.*?</style>", "", text, flags=re.DOTALL)
        text = re.sub(r"<.*?>", "\n", text)
        text = html.unescape(text)

        lines = [line.strip() for line in text.split("\n") if line.strip()]
        start = next((i for i, line in enumerate(lines) if re.match(r"^\d+\.$", line)), None)

        if start is None:
            return "Nu am găsit informații relevante pe web."

        summary = " ".join(lines[start:start + 40])
        if len(summary) < 50:
            return "Nu am găsit informații relevante pe web."

        return summary[:1500]

    except Exception as e:
        return f"Eroare la căutarea pe internet: {e}"


WEB_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Caută informații actualizate pe internet și aduce textul de pe pagini.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Termenul de căutare pe internet"}
                },
                "required": ["query"],
            },
        },
    },
]
