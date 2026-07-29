import os

from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

MODEL_NAME = "qwen2.5-coder:7b"
VISION_MODEL_NAME = "moondream"
OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
DESKTOP_DIR = os.path.join(os.path.expanduser("~"), "Desktop")
MAX_STEPS_PER_TURN = 10
