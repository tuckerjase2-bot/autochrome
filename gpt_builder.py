import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()

# Use the Chat Completions endpoint; model name is configurable (placeholder `gpt-5-nano`).
API_URL = "https://api.openai.com/v1/chat/completions"


def _extract_json(text: str) -> dict | None:
    """Try to extract a JSON object from free-form text.

    Returns the parsed dict or None if parsing fails.
    """
    try:
        return json.loads(text)
    except Exception:
        # Try to find a JSON-looking substring
        m = re.search(r"\{[\s\S]*\}\s*$", text)
        if not m:
            m = re.search(r"\{[\s\S]*\}", text)
        if m:
            s = m.group(0)
            try:
                return json.loads(s)
            except Exception:
                return None
        return None


def generate_plan(prompt: str, api_key: str | None = None, model: str = "gpt-5-nano") -> dict:
    """Generate a Playwright automation plan from a natural-language prompt using OpenAI Chat.

    - Reads API key from `api_key` arg or the environment variable `dOPENAI_KEY_LOL`.
    - Returns a dict with a `steps` list. On failure, returns a safe fallback plan.
    """
    key = api_key or os.getenv("dOPENAI_KEY_LOL") or os.getenv("OPENAI_API_KEY") or "YOUR_API_KEY_HERE"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    system_msg = (
        "You are an assistant that returns a single valid JSON object describing a Playwright "
        "automation plan. The JSON must contain a top-level key `steps` which is a list of step objects. "
        "Each step should include an `action` such as `navigate`, `click`, `input`, `wait`, `screenshot`, or `extract`. "
        "Respond with only the JSON and nothing else."
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 800,
        "temperature": 0.2,
    }

    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        j = resp.json()
        # chat completions: choices[0].message.content
        content = ""
        if isinstance(j.get("choices"), list) and j["choices"]:
            content = j["choices"][0].get("message", {}).get("content", "")
        else:
            content = j.get("text", "")

        plan = _extract_json(content)
        if plan is not None:
            return plan
        # fallback: try parsing any code block JSON inside
        return {
            "steps": [
                {"action": "navigate", "url": "https://example.com"},
                {"action": "click", "selector": "#example", "times": 1}
            ]
        }
    except Exception:
        # On any error, return a conservative fallback plan
        return {
            "steps": [
                {"action": "navigate", "url": "https://example.com"},
                {"action": "click", "selector": "#example", "times": 1}
            ]
        }
