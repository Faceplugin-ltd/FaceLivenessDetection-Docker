"""Gradio demo — Face Liveness (local only).

Upload or capture a face photo, then Check liveness: a Live / Spoof verdict with
the score, the pass line, timing, a Result table and the Raw JSON response.
"""

from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path

import gradio as gr
import requests

import demo_ui

ROOT = Path(__file__).resolve().parent
SAMPLES = ROOT / "assets" / "examples" / "samples"

# ---- product settings (the only lines that differ between Face Liveness repos)
PRODUCT = "Face Liveness"
EDITION = "Standard"
DEFAULT_API_PORT = "8093"
DEFAULT_DEMO_PORT = "9093"
START_HINT = "./run.sh"
# ----

PASS_SCORE = 0.5  # score >= 0.5 is Real (see README)
API = os.environ.get(
    "API_BASE",
    f"http://127.0.0.1:{os.environ.get('PORT', os.environ.get('FACESDK_PORT', DEFAULT_API_PORT))}",
).rstrip("/")
DEMO_PORT = int(os.environ.get("DEMO_PORT", DEFAULT_DEMO_PORT))
esc = demo_ui.esc


def _b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def _liveness_examples() -> list[str]:
    images = demo_ui.list_images(SAMPLES)
    named = [str(p) for p in images if p.stem.lower().startswith(("real", "fake", "spoof_"))]
    return named or [str(p) for p in images]


def _license_status() -> tuple[bool, dict]:
    try:
        r = requests.get(f"{API}/api/licenseStatus", timeout=5)
        body = r.json() if r.ok else {}
        data = body.get("data") if isinstance(body, dict) else None
        return True, data if isinstance(data, dict) else {}
    except Exception:  # noqa: BLE001
        return False, {}


def header_html() -> str:
    online, status = _license_status()
    return demo_ui.header_html(PRODUCT, EDITION, API, status=status, online=online)


def _score_bar(score: float) -> str:
    pct = max(0.0, min(1.0, score)) * 100
    below = " below" if score < PASS_SCORE else ""
    return (f'<span class="fp-score"><span class="fp-track" style="flex-basis:160px">'
            f'<span class="fp-fill{below}" style="width:{pct:.0f}%"></span>'
            f'<span class="fp-mark" style="left:{PASS_SCORE * 100:.0f}%"></span></span>{score:.4f}</span>')


def idle_html() -> str:
    return demo_ui.verdict_html("idle", "No result yet",
                                "Upload or capture a face photo, or pick a sample, then press Check liveness.")


def check_liveness(path):
    online, status = _license_status()
    if not online:
        return demo_ui.verdict_html("bad", "API offline", f"Start the API with {START_HINT} first."), [], ""
    if not status.get("licensed"):
        return demo_ui.verdict_html("warn", "Not licensed", "Activate with your license key first."), [], ""
    if not status.get("liveness"):
        return demo_ui.verdict_html("warn", "Liveness is not on this license"), [], ""
    if not path:
        return demo_ui.verdict_html("warn", "Choose a photo first"), [], ""
    started = time.perf_counter()
    try:
        r = requests.post(f"{API}/api/liveness", json={"image": _b64(path)}, timeout=180)
        payload = r.json()
    except Exception as ex:  # noqa: BLE001
        return demo_ui.verdict_html("bad", "Request failed", esc(ex)), [], ""
    elapsed = (time.perf_counter() - started) * 1000
    raw = json.dumps(payload, indent=2, ensure_ascii=False)
    if not isinstance(payload, dict):
        return demo_ui.verdict_html("bad", "Unexpected response"), [], raw
    if payload.get("licenseError") or payload.get("success") is False:
        msg = str(payload.get("licenseError") or payload.get("message") or "Request failed")
        key = msg.strip().upper().replace("_", " ")
        if key == "NO FACE" or msg.strip().upper() == "NO_FACE":
            return demo_ui.verdict_html("warn", "No face found",
                                       "Use a clear, front-facing photo of one person."), [], raw
        if key in ("IMAGE NOT SUITABLE", "INVALID IMAGE", "IMAGE REQUIRED"):
            return demo_ui.verdict_html(
                "warn",
                "Image not suitable",
                "Please use a higher-resolution photo with your face clearly visible, "
                "uncropped, and large enough in the frame.",
            ), [], raw
        if key == "MULTIPLE FACES":
            return demo_ui.verdict_html("warn", "More than one face",
                                       "Use a clear, front-facing photo of one person."), [], raw
        return demo_ui.verdict_html("warn", msg), [], raw

    data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    score = data.get("score")
    passed = data.get("pass")
    result = str(data.get("result") or "")
    if not isinstance(score, (int, float)):
        message = data.get("message") or payload.get("message") or "No face found. Use a clear photo of one face."
        return demo_ui.verdict_html("warn", str(message)), demo_ui.flatten_rows(data, source="api"), raw

    live = passed is True or (passed is None and score >= PASS_SCORE)
    verdict = demo_ui.verdict_html(
        "ok" if live else "bad",
        "Live person" if live else "Spoof detected",
        "Real face in front of the camera." if live
        else "Looks like a photo, screen, or mask (presentation attack).",
        big=f"{score:.4f}",
    )
    details = (
        '<ul class="fp-checks">'
        f"<li><span>Liveness score</span>{_score_bar(float(score))}</li>"
        f"<li><span>Pass line</span><span>{PASS_SCORE:.4f}</span></li>"
        f"<li><span>Result</span><span>{esc(result or ('Real' if live else 'Spoof'))}</span></li>"
        f"<li><span>Pass</span><span>{'Yes' if live else 'No'}</span></li>"
        "</ul>"
    )
    metrics = demo_ui.metrics_html([("Round trip", f"{elapsed:.0f} ms"), ("Photo", Path(path).name)])
    rows = [["score", f"{score:.4f}", "api"], ["result", result, "api"], ["pass", str(passed), "api"]]
    rows += [r for r in demo_ui.flatten_rows(data, source="api") if r[0] not in ("score", "result", "pass")]
    return verdict + details + metrics, rows, raw


EXAMPLES = _liveness_examples()

with gr.Blocks(title=f"FacePlugin {PRODUCT}", fill_width=True) as demo:
    header = gr.HTML(header_html())
    demo_ui.consent_row()
    gr.HTML('<p class="fp-intro"><strong>Passive liveness</strong> from a single photo: is this a live person, '
            "or a printed photo, screen replay, or mask? No user action needed.</p>")

    with gr.Row(equal_height=False):
        with gr.Column(scale=5, elem_classes=["fp-panel"]):
            liv_in = gr.Image(type="filepath", label="Face photo", sources=["upload", "webcam", "clipboard"], height=340)
            if EXAMPLES:
                gr.Examples(EXAMPLES, inputs=liv_in, label="Spoof samples")
            liv_btn = gr.Button("Check liveness", elem_classes=["primary"], size="lg")
        with gr.Column(scale=6, elem_classes=["fp-panel"]):
            liv_verdict = gr.HTML(idle_html())
            with gr.Tabs():
                with gr.Tab("Result"):
                    liv_table = demo_ui.result_dataframe(headers=["Field", "Value", "Source"], label="Response fields")
                with gr.Tab("Raw JSON"):
                    liv_raw = gr.Code(language="json", label="API response")

    liv_btn.click(check_liveness, inputs=liv_in, outputs=[liv_verdict, liv_table, liv_raw])
    liv_btn.click(header_html, outputs=[header])
    demo.load(header_html, outputs=[header])

if __name__ == "__main__":
    print(f"Gradio demo -> http://127.0.0.1:{DEMO_PORT}  (API {API})")
    demo_ui.launch(demo, DEMO_PORT, server_name="0.0.0.0")
