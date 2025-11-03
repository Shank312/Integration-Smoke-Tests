import json, os, time
from pathlib import Path
from typing import Any, Dict
import requests

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000").rstrip("/")
CHAT_PATH = os.getenv("CHAT_PATH", "/chat")
RESULTS_JSON_PATH = os.getenv("RESULTS_JSON_PATH", "./results.json")
TIMEOUT_SECS = float(os.getenv("TIMEOUT_SECS", "60"))

def post_chat(q: str) -> Dict[str, Any]:
    url = f"{BASE_URL}{CHAT_PATH}"
    headers = {"Content-Type":"application/json"}
    payload = {"message": q, "metadata": {"source":"e2e_smoke_test","tags":["e2e","smoke"]}, "stream": False}
    r = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT_SECS)
    assert r.status_code == 200, f"POST {url} failed: {r.status_code} {r.text}"
    return r.json()

def get_text(d: Dict[str, Any]) -> str:
    for key in ("answer","content"):
        if isinstance(d.get(key), str) and d[key].strip(): return d[key].strip()
    if isinstance(d.get("message"), dict) and isinstance(d["message"].get("content"), str):
        t = d["message"]["content"].strip()
        if t: return t
    for v in d.values():
        if isinstance(v, str) and v.strip(): return v.strip()
    raise AssertionError(f"No text in response keys={list(d.keys())}")

def flatten(obj: Any, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k,v in obj.items():
            out |= flatten(v, f"{prefix}.{k}" if prefix else k)
    elif isinstance(obj,(int,float)):
        out[prefix] = float(obj)
    return out

def test_e2e_smoke():
    data = post_chat("Wire chatbot → rag-system → llm-agent using prompt layer. One sentence summary.")
    text = get_text(data)
    assert len(text) > 0

    p = Path(RESULTS_JSON_PATH)
    assert p.exists(), f"results.json not found at {p.resolve()}"
    res = json.loads(p.read_text(encoding="utf-8"))
    flat = flatten(res)

    thresholds = json.loads(os.getenv("EVAL_THRESHOLDS",'{"overall.score":0.6,"faithfulness":0.7}'))
    missing = [k for k in thresholds if k not in flat]
    assert not missing, f"Missing metrics: {missing}. Have: {sorted(flat.keys())}"

    failures = [f"{k}: {flat[k]:.4f} < {thr:.4f}" for k,thr in thresholds.items() if flat[k] < thr]
    assert not failures, "Thresholds not met → " + ", ".join(failures)
