import json
import urllib.parse
import urllib.request


def get_current_weather(city: str) -> str:
    try:
        print(f"\nVerific vremea pentru '{city}'...")

        encoded_city = urllib.parse.quote(city)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_city}&count=1&language=ro"

        with urllib.request.urlopen(geo_url, timeout=10) as response:
            geo = json.loads(response.read().decode("utf-8"))

        results = geo.get("results")
        if not results:
            return f"Nu am găsit orașul '{city}'."

        location = results[0]
        latitude, longitude = location["latitude"], location["longitude"]
        found_name = location.get("name", city)

        forecast_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}&longitude={longitude}&current_weather=true"
        )
        with urllib.request.urlopen(forecast_url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        current = data.get("current_weather")
        if not current:
            return f"Nu am putut obține vremea pentru {found_name}."

        return (
            f"În {found_name}, temperatura curentă este {current['temperature']}°C, "
            f"viteza vântului {current['windspeed']} km/h "
            f"(ora locală a datelor: {current['time']})."
        )

    except Exception as e:
        return f"Eroare la obținerea vremii: {e}"


WEATHER_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": (
                "Obține temperatura și vremea exactă, în timp real, pentru un oraș. "
                "Folosește întotdeauna această unealtă (nu search_web) pentru "
                "întrebări despre temperatură, grade sau vreme curentă."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "Numele orașului, ex: București"}
                },
                "required": ["city"],
            },
        },
    },
]
