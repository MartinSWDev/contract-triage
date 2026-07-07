"""LLM adapter: Anthropic API if credentials are available, otherwise the
`claude` CLI in headless mode (which reuses the local Claude Code login).

The adapter is deliberately one small file: routing sensitive contracts to a
different backend (e.g. a self-hosted model) means swapping this file only.
"""
import json
import os
import re
import subprocess

MODEL = os.environ.get("TRIAGE_MODEL", "claude-opus-4-8")


def _backend():
    if os.environ.get("TRIAGE_BACKEND"):  # "api" | "cli"
        return os.environ["TRIAGE_BACKEND"]
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return "api"
    return "cli"


def _call_api(system, prompt, schema):
    import anthropic
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=system,
        output_config={"format": {"type": "json_schema", "schema": schema}},
        messages=[{"role": "user", "content": prompt}],
    )
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


def _call_cli(system, prompt, schema):
    full = (
        f"{system}\n\n{prompt}\n\n"
        "Respond with a single JSON object matching this JSON Schema, and "
        "nothing else - no markdown fences, no commentary:\n"
        + json.dumps(schema)
    )
    result = subprocess.run(
        ["claude", "-p", full, "--model", MODEL, "--output-format", "json",
         "--max-turns", "1"],
        capture_output=True, text=True, timeout=900,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"claude CLI failed (rc={result.returncode}): "
            f"stderr={result.stderr[:1000]} stdout={result.stdout[:1000]}")
    payload = json.loads(result.stdout)
    text = payload.get("result", "")
    # Strip accidental fences and grab the outermost JSON object.
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object in model output: {text[:500]}")
    return json.loads(text[start:end + 1])


def analyze_json(system, prompt, schema):
    """Return the model's analysis as a parsed dict, retrying once on bad JSON."""
    backend = _backend()
    call = _call_api if backend == "api" else _call_cli
    last_err = None
    for _ in range(3):
        try:
            return call(system, prompt, schema), backend
        except (json.JSONDecodeError, ValueError, RuntimeError) as e:
            last_err = e
    raise RuntimeError(f"Model call failed after 3 attempts: {last_err}")
