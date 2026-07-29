import base64
import json
import os
import re
import urllib.parse
import urllib.request

from config import client, MODEL_NAME, VISION_MODEL_NAME, OLLAMA_GENERATE_URL, DESKTOP_DIR


def _clean_image_query(query: str) -> str:
    text = query.strip().lower()
    text = re.sub(r"^(o |un |niște |niste )?(poz[aă]|imagine|fotografi[ae])( a)?( cu)?\s+", "", text)
    text = re.sub(r"^(o |un )\s*", "", text)
    return text.strip() or query


def _search_openverse(term: str, flickr_only: bool):
    encoded_term = urllib.parse.quote(term)
    url = f"https://api.openverse.org/v1/images/?q={encoded_term}&page_size=8&extension=jpg,jpeg,png"
    if flickr_only:
        url += "&source=flickr"

    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data.get("results") or []


def _describe_image(image_bytes: bytes) -> str:
    payload = {
        "model": VISION_MODEL_NAME,
        "prompt": "Describe this image in one short sentence.",
        "images": [base64.b64encode(image_bytes).decode("utf-8")],
        "stream": False,
    }
    request = urllib.request.Request(
        OLLAMA_GENERATE_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        data = json.loads(response.read().decode("utf-8"))
    return (data.get("response") or "").strip()


def _image_matches(description: str, term: str) -> bool:
    if not description:
        return False
    try:
        reply = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Răspunzi STRICT cu DA sau NU, fără alte cuvinte."},
                {
                    "role": "user",
                    "content": (
                        f'Descrierea unei imagini este: "{description}". '
                        f'Aceasta descriere arată un/o "{term}"? Răspunde DA sau NU.'
                    ),
                },
            ],
            temperature=0,
        )
        return (reply.choices[0].message.content or "").strip().upper().startswith("DA")
    except Exception:
        return True


def download_image(query: str, filename: str = "") -> str:
    try:
        term = _clean_image_query(query)
        print(f"\nCaut imagine: '{term}'...")

        results = _search_openverse(term, flickr_only=True) or _search_openverse(term, flickr_only=False)
        if not results:
            return f"Nu am găsit nicio imagine pentru '{term}'."

        last_description = ""

        for candidate in results[:5]:
            image_url = candidate["url"]

            try:
                request = urllib.request.Request(image_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(request, timeout=20) as response:
                    content = response.read()
            except Exception:
                continue

            print(f"\nVerific vizual: {image_url}")
            description = _describe_image(content)
            last_description = description or last_description

            if not _image_matches(description, term):
                print(f"Nu se potrivește ({description!r}), încerc următoarea imagine...")
                continue

            extension = os.path.splitext(urllib.parse.urlparse(image_url).path)[1] or ".jpg"
            final_name = filename or re.sub(r"[^\w\-]", "_", term)[:40] + extension
            full_path = os.path.join(DESKTOP_DIR, final_name)

            with open(full_path, "wb") as f:
                f.write(content)

            return f"Am descărcat imaginea la: {full_path}\nVerificare vizuală: {description}"

        return (
            f"Am găsit rezultate pentru '{term}', dar niciuna nu a trecut verificarea vizuală "
            f"(ultima imagine arăta: {last_description!r}). Nu am descărcat nimic."
        )

    except Exception as e:
        return f"Eroare la descărcarea imaginii: {e}"


IMAGES_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "download_image",
            "description": (
                "Caută o imagine (cu licență deschisă, via Openverse), o verifică vizual cu "
                "un model local de computer vision (ca să confirme că arată chiar ce s-a cerut, "
                "nu ceva irelevant), și o descarcă direct pe Desktop-ul utilizatorului."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Ce imagine să caute, ex: 'vulpe'"},
                    "filename": {
                        "type": "string",
                        "description": "Nume opțional pentru fișier, ex: vulpe.jpg",
                    },
                },
                "required": ["query"],
            },
        },
    },
]
