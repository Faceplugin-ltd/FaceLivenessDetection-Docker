#!/usr/bin/env python3
"""Parse JSON or multipart/form-data for FacePlugin HTTP process routes.

Same field names for both body types. Images in form-data are files; the helper
returns base64 strings so existing sdk.py calls stay unchanged.
"""

from __future__ import annotations

import base64
import json
from typing import Any

from flask import request


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on")
    return bool(value)


def _file_b64(*names: str) -> str | None:
    for name in names:
        uploaded = request.files.get(name)
        if uploaded is None:
            continue
        data = uploaded.read()
        if data:
            return base64.b64encode(data).decode("ascii")
    return None


def _files_b64(name: str) -> list[str]:
    out: list[str] = []
    for uploaded in request.files.getlist(name):
        data = uploaded.read()
        if data:
            out.append(base64.b64encode(data).decode("ascii"))
    return out


def _maybe_json(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    text = value.strip()
    if text[:1] in "{[":
        try:
            return json.loads(text)
        except Exception:  # noqa: BLE001
            return value
    return value


def is_multipart() -> bool:
    ctype = (request.content_type or "").lower()
    return "multipart/form-data" in ctype


def parse_body() -> dict[str, Any]:
    """Dict with the same keys as the JSON body; image fields are base64."""
    if not is_multipart():
        data = request.get_json(silent=True)
        return data if isinstance(data, dict) else {}

    out: dict[str, Any] = {}
    for key, value in request.form.items():
        out[key] = _maybe_json(value)

    image = _file_b64("image", "file")
    if image:
        out["image"] = image
    image1 = _file_b64("image1")
    if image1:
        out["image1"] = image1
    image2 = _file_b64("image2")
    if image2:
        out["image2"] = image2
    rfid = _file_b64("rfid")
    if rfid:
        out["rfid"] = rfid

    images = _files_b64("images")
    if images:
        out["images"] = images
    elif "image" in out and "images" not in out:
        out["images"] = [out["image"]]

    return out


def crop_flag(data: dict[str, Any]) -> bool:
    return _truthy(data.get("cropImage") or data.get("crop_image"))


def activate_license_bytes() -> bytes | None:
    if is_multipart():
        uploaded = request.files.get("license")
        if uploaded is not None:
            data = uploaded.read()
            if data:
                return data
        text = (request.form.get("license") or "").strip()
        if text:
            return text.encode("utf-8")
        return None
    import license_ux

    return license_ux.decode_activate_body(request.get_data() or b"")
