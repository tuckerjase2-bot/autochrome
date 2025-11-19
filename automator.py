import time
import json
import logging
from typing import Dict, Any
from playwright.sync_api import sync_playwright

logger = logging.getLogger("automator")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")


def run_plan(plan: Dict[str, Any], headless: bool = True, log_file: str = "run.log") -> Dict[str, Any]:
    """Execute an automation plan.

    Plan example:
    {
      "steps": [
        {"action": "navigate", "url": "https://example.com"},
        {"action": "click", "selector": "#login", "times": 1, "delay": 0.5},
        {"action": "input", "selector": "#user", "value": "alice"},
        {"action": "wait", "seconds": 1},
        {"action": "screenshot", "path": "out.png"},
        {"action": "extract", "selector": "h1", "name": "title"}
      ]
    }

    Returns a dict with variables collected and a status.
    """
    logger.info("Starting automation plan")
    variables: Dict[str, str] = {}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=headless)
            context = browser.new_context()
            page = context.new_page()

            for idx, step in enumerate(plan.get("steps", []), start=1):
                action = step.get("action")
                logger.info(f"Step {idx}: {action}")
                if action == "navigate":
                    url = step.get("url")
                    logger.info(f"Navigating to {url}")
                    page.goto(url)
                elif action == "click":
                    selector = step.get("selector")
                    times = int(step.get("times", 1))
                    delay = float(step.get("delay", 0.5))
                    for i in range(times):
                        logger.info(f"Clicking {selector} ({i+1}/{times})")
                        page.click(selector)
                        time.sleep(delay)
                elif action == "input":
                    selector = step.get("selector")
                    value = str(step.get("value", ""))
                    logger.info(f"Filling {selector} with: {value}")
                    page.fill(selector, value)
                elif action == "wait":
                    secs = float(step.get("seconds", 1))
                    logger.info(f"Waiting {secs} seconds")
                    time.sleep(secs)
                elif action == "screenshot":
                    path = step.get("path", f"screenshot-{int(time.time())}.png")
                    logger.info(f"Taking screenshot to {path}")
                    page.screenshot(path=path)
                elif action == "extract":
                    selector = step.get("selector")
                    name = step.get("name") or f"var_{len(variables)+1}"
                    logger.info(f"Extracting text from {selector} into variable '{name}'")
                    try:
                        el = page.query_selector(selector)
                        text = el.inner_text() if el else ""
                    except Exception:
                        text = ""
                    variables[name] = text
                else:
                    logger.warning(f"Unknown action: {action}")

            browser.close()
    except Exception as e:
        logger.exception("Automation failed")
        result = {"status": "error", "error": str(e), "variables": variables}
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(result) + "\n")
        return result

    result = {"status": "done", "variables": variables}
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(result) + "\n")
    logger.info("Plan finished")
    return result
