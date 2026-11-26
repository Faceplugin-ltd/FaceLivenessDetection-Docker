#!/usr/bin/env python3
"""
Shared Gradio demo helpers and theme for FacePlugin product demos (local only).

Canonical copy: templates/linux-api/demo_ui.py
Every product repo keeps an identical copy next to its demo (demo_ui.py, or
demo/ui.py for the ID Document products). Change the canonical copy, then copy it.

UI conventions (every product demo):
  - Header: brand, product, edition · platform, license badge, API docs link
  - Consent note: data stays on this computer (dismissed once per browser)
  - Panels: input on the left, result on the right
  - Verdict card on top of every result (ok / warn / bad), then Result table + Raw JSON
  - Examples: every image under assets/examples/samples/ (or examples/)
"""

from __future__ import annotations

import base64
import html
import io
import json
import platform
from pathlib import Path
from typing import Any

import gradio as gr

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

# ---------------------------------------------------------------- theme

# Result tables and galleries grow with content; the page scrolls. No inner viewport.
RESULT_CSS = """
.fp-result-table, .fp-result-table .table-wrap, .fp-result-table .wrap,
.fp-result-table .overflow-y-auto, .fp-result-table .overflow-auto {
  max-height: none !important; height: auto !important; overflow: visible !important; }
.fp-result-table table { table-layout: fixed !important; width: 100% !important; }
.fp-result-table th, .fp-result-table td { white-space: normal !important; overflow-wrap: anywhere !important;
  word-break: break-word !important; vertical-align: top !important; }
.fp-result-gallery, .fp-result-gallery .grid-wrap, .fp-result-gallery .gallery-container,
.fp-result-gallery .overflow-y-auto, .fp-result-gallery .overflow-auto {
  max-height: none !important; height: auto !important; overflow: visible !important; }
"""

THEME_CSS = RESULT_CSS + """
:root {
  --bg: #eef1f4; --card: #fff; --line: #d5dde6; --line-soft: #e6ebf0;
  --text: #142033; --muted: #5a6b7e; --brand: #0f3d75; --brand-soft: #e8eef6;
  --ok-bg: #e5f4eb; --ok: #0d6a3a; --warn-bg: #f8f0dc; --warn: #6b5420;
  --danger: #b42318; --danger-soft: #fdecea; --chip: #f6f8fa;
}
.gradio-container { max-width: 1240px !important; margin: 0 auto !important;
  background: var(--bg) !important; color: var(--text) !important;
  font-family: Inter, "Segoe UI", system-ui, sans-serif !important; }
footer, .footer { display: none !important; }
.fp-consent-ok #fp-consent { display: none !important; }
#fp-settings { align-self: center !important; height: auto !important; max-height: 36px; }

/* header */
.fp-bar { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; padding: 10px 2px; }
.fp-brand { display: flex; align-items: center; }
.fp-logo { height: 28px; width: auto; display: block; }
.fp-product { font-weight: 600; font-size: 16px; color: var(--text); }
.fp-spacer { flex: 1; }
.fp-badge, .fp-id, .fp-count, .fp-tag-live, .fp-tag-spoof, .fp-tag-warn {
  display: inline-flex; align-items: center; gap: 4px; padding: 1px 9px; border-radius: 999px;
  font-size: 12px; font-weight: 500; line-height: 20px; white-space: nowrap; font-variant-numeric: tabular-nums; }
.fp-badge { background: var(--brand-soft); color: var(--brand); }
.fp-badge.ok { background: var(--ok-bg); color: var(--ok); }
.fp-badge.bad { background: var(--danger-soft); color: var(--danger); }
.fp-id { background: var(--brand-soft); color: var(--brand); }
.fp-count { background: var(--chip); color: var(--muted); border: 1px solid var(--line); }
.fp-tag-live { background: var(--ok-bg); color: var(--ok); }
.fp-tag-spoof { background: var(--danger-soft); color: var(--danger); }
.fp-tag-warn { background: var(--warn-bg); color: var(--warn); }
.fp-link { color: var(--brand); font-size: 13px; text-decoration: none; }
.fp-link:hover { text-decoration: underline; }
#fp-consent { background: var(--brand-soft) !important; border-radius: 10px !important; padding: 6px 12px !important; align-items: center !important; }
#fp-consent p { margin: 0; color: var(--brand); font-size: 13px; }
.fp-intro { margin: 2px 0 0; color: var(--muted); font-size: 14px; }
.fp-intro strong { color: var(--text); }

/* panels */
.fp-panel { background: var(--card) !important; border: 1px solid var(--line) !important; border-radius: 12px !important; padding: 16px !important; }
.fp-h2 { margin: 0; font-size: 15px; font-weight: 600; color: var(--text); display: flex; align-items: center; gap: 8px; }
.fp-muted { color: var(--muted); font-size: 13px; margin: 0; }
.fp-empty { margin: 28px 0; color: var(--muted); text-align: center; }
.fp-click { all: unset; box-sizing: border-box; cursor: pointer; }
.fp-click:focus-visible { outline: 2px solid var(--brand); outline-offset: 2px; border-radius: 10px; }
.fp-textlink { all: unset; cursor: pointer; color: var(--brand); font-size: 13px; font-weight: 500; }
.fp-textlink:hover { text-decoration: underline; }
.fp-textlink.danger { color: var(--danger); }

/* verdict */
.fp-verdict { display: flex; align-items: center; gap: 12px; padding: 12px 14px; border-radius: 10px; margin: 0 0 12px; }
.fp-verdict.ok { background: var(--ok-bg); color: var(--ok); }
.fp-verdict.warn { background: var(--warn-bg); color: var(--warn); }
.fp-verdict.bad { background: var(--danger-soft); color: var(--danger); }
.fp-verdict.idle { background: var(--chip); color: var(--muted); }
.fp-verdict strong { font-size: 16px; }
.fp-verdict .fp-detail { font-size: 13px; opacity: .9; }
.fp-verdict .fp-big { margin-left: auto; font-size: 22px; font-weight: 600; font-variant-numeric: tabular-nums; }

/* faces, candidates, metrics */
.fp-face { border: 1px solid var(--line); border-radius: 12px; padding: 14px; margin-bottom: 12px; }
.fp-pair { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.fp-shot { margin: 0; display: block; width: 100%; }
.fp-shot img, .fp-noimg { width: 100%; aspect-ratio: 1; object-fit: cover; object-position: center 30%;
  border-radius: 10px; background: #e7edf3; display: block; }
.fp-noimg { display: grid; place-items: center; color: var(--muted); font-size: 13px; }
.fp-cap { margin: 6px 0 0; color: var(--muted); font-size: 13px; display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
.fp-label { margin: 0 0 6px; font-size: 11px; font-weight: 600; color: var(--brand); text-transform: uppercase; letter-spacing: .05em; }
.fp-notes { margin: 10px 0 0; padding: 8px 10px; border-radius: 8px; background: var(--chip); font-size: 13px; color: var(--muted); }
.fp-metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 8px; margin-top: 4px; }
.fp-metric { background: var(--chip); border-radius: 8px; padding: 8px 10px; }
.fp-k { margin: 0; color: var(--muted); font-size: 12px; }
.fp-v { margin: 2px 0 0; font-size: 16px; font-weight: 600; font-variant-numeric: tabular-nums; overflow-wrap: anywhere; }
.fp-rows { margin: 8px 0 0; display: flex; flex-direction: column; }
.fp-row { display: grid; grid-template-columns: 22px 36px minmax(0,1fr) 130px; gap: 10px; align-items: center;
  width: 100%; padding: 7px 8px; border-top: 1px solid var(--line-soft); font-size: 14px; }
.fp-row:hover { background: #f5f8fc; border-radius: 8px; }
.fp-row.top { background: #f1f6fd; border-radius: 8px; border-top-color: transparent; }
.fp-rank { color: var(--muted); font-size: 13px; text-align: center; }
.fp-avatar { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; object-position: center 30%; background: #e7edf3; display: block; }
.fp-name { display: flex; align-items: center; gap: 8px; min-width: 0; }
.fp-name span:first-child { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.fp-score { display: flex; align-items: center; gap: 8px; justify-content: flex-end; font-weight: 600; font-variant-numeric: tabular-nums; }
.fp-track { position: relative; display: block; flex: 0 0 60px; height: 6px; border-radius: 3px; background: var(--line-soft); }
.fp-fill { display: block; height: 100%; background: var(--brand); border-radius: 3px; }
.fp-fill.below { background: #9aa8b8; }
.fp-mark { position: absolute; top: -3px; width: 2px; height: 12px; background: var(--text); opacity: .55; }
.fp-list-head { display: flex; justify-content: space-between; align-items: center; margin-top: 14px; color: var(--muted); font-size: 12px; }
.fp-checks { margin: 0; padding: 0; list-style: none; }
.fp-checks li { display: flex; justify-content: space-between; gap: 12px; padding: 6px 2px; border-top: 1px solid var(--line-soft); font-size: 14px; }
.fp-checks li:first-child { border-top: 0; }

/* gallery grid */
.fp-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(118px, 1fr)); gap: 10px; margin-top: 8px; }
.fp-card { border: 1px solid var(--line); border-radius: 10px; padding: 6px; background: #fff; width: 100%; }
.fp-card:hover { border-color: var(--brand); }
.fp-card img, .fp-card .fp-noimg { width: 100%; aspect-ratio: 1; object-fit: cover; object-position: center 30%; border-radius: 7px; background: #e7edf3; display: block; }
.fp-card-name { margin: 6px 2px 0; font-size: 13px; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.fp-card-meta { margin: 2px 2px 0; font-size: 12px; color: var(--muted); display: flex; justify-content: space-between; }
.fp-pager { align-items: center !important; }

/* progress queue */
.fp-progress { margin: 4px 0 8px; }
.fp-progress-track { height: 8px; border-radius: 4px; background: var(--line-soft); overflow: hidden; margin-top: 6px; }
.fp-progress-fill { height: 100%; background: var(--brand); transition: width .2s; }
.fp-queue { border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }
.fp-q { display: grid; grid-template-columns: 34px minmax(0,1fr) auto; gap: 10px; align-items: center; padding: 6px 10px; border-top: 1px solid var(--line-soft); font-size: 13px; }
.fp-q:first-child { border-top: 0; }
.fp-q img { width: 34px; height: 34px; border-radius: 6px; object-fit: cover; display: block; background: #e7edf3; }
.fp-q-file { color: var(--muted); font-size: 12px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.fp-st { font-size: 12px; font-weight: 500; white-space: nowrap; }
.fp-st.ok { color: var(--ok); } .fp-st.warn { color: var(--warn); } .fp-st.bad { color: var(--danger); } .fp-st.wait { color: var(--muted); }
.fp-counts { display: flex; gap: 8px; flex-wrap: wrap; margin: 8px 0; }

/* dialogs */
.fp-modal { position: fixed !important; inset: 0; z-index: 1000; padding: 24px; background: rgba(15,23,42,.45);
  display: flex !important; align-items: center; justify-content: center; overflow-y: auto; }
.fp-modal.fp-top { z-index: 1010; }
.fp-dialog { background: var(--card) !important; border-radius: 14px; padding: 20px !important; width: min(760px, 100%) !important;
  max-width: 760px; flex: 0 1 auto !important; max-height: calc(100vh - 48px); overflow-y: auto; margin: auto;
  box-shadow: 0 24px 64px rgba(15,23,42,.25); }
.fp-dialog.narrow { width: min(520px, 100%) !important; max-width: 520px; }
.fp-dialog-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.fp-modal-close, .fp-x { flex: 0 0 auto !important; min-width: 0 !important; }
.fp-photos { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 10px; margin-top: 12px; }
.fp-photo { border: 1px solid var(--line); border-radius: 10px; padding: 6px; }
.fp-photo img { width: 100%; aspect-ratio: 1; object-fit: cover; object-position: center 30%; border-radius: 7px; display: block; }
.fp-photo-meta { display: flex; justify-content: space-between; align-items: center; margin-top: 6px; font-size: 12px; color: var(--muted); }
.fp-alert { margin: 8px 0 0; padding: 10px 12px; border-radius: 8px; font-size: 14px; }
.fp-alert.warn { background: var(--warn-bg); color: var(--warn); }
.fp-alert.danger { background: var(--danger-soft); color: var(--danger); }
.fp-alert.ok { background: var(--ok-bg); color: var(--ok); }
.fp-pairs .fp-pairrow { display: grid; grid-template-columns: minmax(0,1fr) 90px minmax(0,1fr); gap: 10px; align-items: center; padding: 8px 0; border-top: 1px solid var(--line-soft); }
.fp-pairs .fp-pairside { display: flex; align-items: center; gap: 8px; min-width: 0; }

/* API tab */
.fp-api table { width: 100%; border-collapse: collapse; font-size: 13px; }
.fp-api td, .fp-api th { text-align: left; padding: 6px 8px; border-top: 1px solid var(--line-soft); vertical-align: top; }
.fp-api code { font-size: 12px; }
.fp-api pre { background: #0f1b2d; color: #e6edf6; padding: 12px; border-radius: 8px; overflow-x: auto; font-size: 12px; }

button.primary, .primary { background: var(--brand) !important; color: #fff !important; border: 0 !important; }
.fp-danger-btn { background: #fff !important; color: var(--danger) !important; border: 1px solid #f1c4bf !important; }
.fp-actions { justify-content: flex-end !important; }
@media (max-width: 760px) {
  .fp-row { grid-template-columns: 22px 36px minmax(0,1fr) 90px; }
}
"""

# Page <head>: remembers the dismissed consent note; a click on a dialog's dimmed
# backdrop presses that dialog's close button.
HEAD_JS = """
<script>
(() => {
  try { if (localStorage.getItem('fpConsent') === '1')
    document.documentElement.classList.add('fp-consent-ok'); } catch (e) {}
  if (window.__fpModalOutside) return;
  window.__fpModalOutside = true;
  document.addEventListener('mousedown', (event) => {
    const modal = event.target.closest('.fp-modal');
    if (!modal || event.target.closest('.fp-dialog')) return;
    const close = modal.querySelector('.fp-modal-close');
    if (close) close.click();
  }, true);
})();
</script>
"""

CONSENT_JS = """() => {
  try { localStorage.setItem('fpConsent', '1'); } catch (e) {}
  document.documentElement.classList.add('fp-consent-ok');
  return [];
}"""

# For gr.HTML(js_on_load=CLICK_JS): clicks on [data-act] reach Python as evt.act / evt.id.
CLICK_JS = """
element.addEventListener('click', (event) => {
  const target = event.target.closest('[data-act]');
  if (!target || !element.contains(target)) return;
  event.preventDefault();
  trigger('click', {act: target.dataset.act, id: target.dataset.id || ''});
});
"""

PLATFORM = "Windows" if platform.system() == "Windows" else "Linux"


def esc(value) -> str:
    return html.escape(str(value if value is not None else ""))


def license_badge(status: dict | None, online: bool = True) -> str:
    """Header badge from GET /api/licenseStatus data."""
    if not online:
        return '<span class="fp-badge bad">API offline</span>'
    status = status or {}
    if status.get("licensed"):
        label = status.get("label") or status.get("levelName") or "Licensed"
        return f'<span class="fp-badge ok">License · {esc(label)}</span>'
    return '<span class="fp-badge bad">Not licensed</span>'


def _logo_uri() -> str:
    """Wordmark for the header. Cached so a refresh does not re-encode the file."""
    cached = getattr(_logo_uri, "value", None)
    if cached is not None:
        return cached
    path = Path(__file__).resolve().parent / "assets" / "logo.png"
    uri = ""
    if path.is_file():
        from PIL import Image

        image = Image.open(path).convert("RGBA")
        image.thumbnail((420, 56), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
    _logo_uri.value = uri
    return uri


def header_html(product: str, edition: str, api: str, *, status: dict | None = None,
                online: bool = True, extra: str = "", docs: bool = False) -> str:
    """Brand bar: logo · product · edition/platform · extra badges · license · links."""
    docs_link = (f'<a class="fp-link" href="{esc(api)}/docs" target="_blank" rel="noopener">API docs</a>'
                 if docs else "")
    logo = _logo_uri()
    brand = f'<img class="fp-logo" src="{logo}" alt="FacePlugin"/>' if logo else "FacePlugin"
    return (
        '<div class="fp-bar"><div class="fp-brand">'
        f'{brand}</div>'
        f'<span class="fp-product">{esc(product)}</span>'
        f'<span class="fp-badge">{esc(edition)} · {PLATFORM}</span>'
        f'<span class="fp-spacer"></span>{extra}{license_badge(status, online)}{docs_link}'
        '<a class="fp-link" href="https://faceplugin.com" target="_blank" rel="noopener">Get a license</a></div>'
    )


def consent_row(text: str = "Photos are processed only on this computer. Nothing is sent to FacePlugin or anyone else."):
    """Dismissible privacy note under the header (remembered per browser)."""
    with gr.Row(elem_id="fp-consent", equal_height=True):
        gr.HTML(f"<p>{esc(text)}</p>", scale=8)
        button = gr.Button("Got it", size="sm", scale=0, min_width=80)
    button.click(None, js=CONSENT_JS)
    return button


def verdict_html(kind: str, title: str, detail: str = "", big: str = "", extra: str = "") -> str:
    """Result headline. kind: ok | warn | bad | idle. `detail` and `extra` are HTML."""
    big_html = f'<span class="fp-big">{esc(big)}</span>' if big else ""
    detail_html = f'<div class="fp-detail">{detail}</div>' if detail else ""
    return (f'<div class="fp-verdict {kind}"><div><strong>{esc(title)}</strong>{detail_html}</div>'
            f"{extra}{big_html}</div>")


def metrics_html(items: list[tuple[str, str]]) -> str:
    cells = "".join(f'<div class="fp-metric"><p class="fp-k">{esc(k)}</p><p class="fp-v">{esc(v)}</p></div>'
                    for k, v in items)
    return f'<div class="fp-metrics">{cells}</div>'


def launch(demo: gr.Blocks, port: int, *, server_name: str = "127.0.0.1", **kwargs) -> None:
    """Launch with the FacePlugin theme."""
    demo.launch(server_name=server_name, server_port=port, css=THEME_CSS, head=HEAD_JS, **kwargs)


# ---------------------------------------------------------------- result widgets


def result_dataframe(*, headers: list[str] | None = None, label: str = "Extracted fields"):
    """Field table that expands with rows (no inner scrollbar)."""
    cols = headers or ["Field", "Value", "Source"]
    kw = dict(
        headers=cols,
        datatype=["str"] * len(cols),
        interactive=False,
        wrap=True,
        label=label,
        elem_classes=["fp-result-table"],
    )
    if len(cols) == 3:
        kw["column_widths"] = ["30%", "50%", "20%"]
    try:
        return gr.Dataframe(**kw, max_height=None)
    except TypeError:
        kw.pop("column_widths", None)
        try:
            return gr.Dataframe(**kw, max_height=None)
        except TypeError:
            return gr.Dataframe(**kw)


def result_gallery(*, label: str = "Images", columns: int = 2):
    """Image grid that expands with items (no inner scrollbar)."""
    kw = dict(
        label=label,
        columns=columns,
        object_fit="contain",
        show_label=True,
        elem_classes=["fp-result-gallery"],
    )
    try:
        return gr.Gallery(**kw, height=None)
    except TypeError:
        return gr.Gallery(**kw)


def samples_dir(root: Path) -> Path:
    for rel in ("assets/examples/samples", "assets/samples", "examples/samples", "examples"):
        p = root / rel
        if p.is_dir():
            return p
    return root / "assets" / "examples" / "samples"


def list_images(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(
        p for p in directory.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES
    )


def list_image_paths(directory: Path) -> list[str]:
    return [str(p) for p in list_images(directory)]


def list_pair_examples(directory: Path) -> list[list[str]]:
    """Match-style pairs: ``pair(N)_1.*`` + ``pair(N)_2.*`` when both exist."""
    files = {p.name: p for p in list_images(directory)}
    pairs: list[list[str]] = []
    seen: set[str] = set()
    for name, path in sorted(files.items()):
        stem = path.stem  # pair(1)_1
        if "_1" not in stem or stem in seen:
            continue
        other_stem = stem.rsplit("_1", 1)[0] + "_2"
        for suf in IMAGE_SUFFIXES:
            other = files.get(other_stem + suf)
            if other:
                pairs.append([str(path), str(other)])
                seen.add(stem)
                seen.add(other_stem)
                break
    return pairs


def cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6g}"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def flatten_rows(
    obj: Any,
    *,
    prefix: str = "",
    source: str = "",
    skip_keys: set[str] | None = None,
    max_rows: int = 200,
) -> list[list[str]]:
    """Flatten nested JSON into [Field, Value, Source] rows."""
    skip = skip_keys or set()
    rows: list[list[str]] = []

    def walk(node: Any, path: str) -> None:
        if len(rows) >= max_rows:
            return
        if isinstance(node, dict):
            for key, value in node.items():
                if key in skip:
                    continue
                child = f"{path}.{key}" if path else str(key)
                if isinstance(value, (dict, list)):
                    # Prefer compact attribute {value, confidence/status}
                    if (
                        isinstance(value, dict)
                        and "value" in value
                        and not any(isinstance(value[k], (dict, list)) for k in value)
                    ):
                        val = value.get("value")
                        extra = []
                        if "confidence" in value:
                            extra.append(f"conf={cell(value['confidence'])}")
                        if "status" in value:
                            extra.append(f"status={cell(value['status'])}")
                        if "range" in value:
                            extra.append(f"range={cell(value['range'])}")
                        shown = cell(val)
                        if extra:
                            shown = f"{shown} ({', '.join(extra)})"
                        rows.append([child, shown, source])
                    else:
                        walk(value, child)
                else:
                    rows.append([child, cell(value), source])
        elif isinstance(node, list):
            if not node:
                rows.append([path or "[]", "[]", source])
                return
            # Short list of scalars
            if all(not isinstance(x, (dict, list)) for x in node):
                rows.append([path, cell(node), source])
                return
            for i, item in enumerate(node):
                walk(item, f"{path}[{i}]")
        else:
            rows.append([path or "value", cell(node), source])

    walk(obj, prefix)
    return rows


def result_outputs(
    payload: Any,
    *,
    summary: str,
    source: str = "api",
    skip_keys: set[str] | None = None,
) -> tuple[str, list[list[str]], str]:
    rows = flatten_rows(payload, source=source, skip_keys=skip_keys)
    raw = json.dumps(payload, indent=2, ensure_ascii=False) if payload is not None else ""
    return summary, rows, raw


def error_outputs(message: str) -> tuple[str, list[list[str]], str]:
    return f"**Error:** {message}", [], ""


def result_panel(*, placeholder: str = "*Run an action to see fields.*"):
    """Create Result + Raw JSON tabs. Returns (summary, table, raw) components."""
    with gr.Tabs():
        with gr.Tab("Result"):
            summary = gr.Markdown(value=placeholder)
            table = result_dataframe()
        with gr.Tab("Raw JSON"):
            raw = gr.Code(language="json", label="API response")
    return summary, table, raw
