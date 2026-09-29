from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from optimizer.infrastructure.demo_loader import resolve_repo_root

CONFIG_REL_PATH = Path("configs") / "visualization_colors.json"

_DEFAULT_GRADIENTS: dict[str, dict[str, str]] = {
    "relevance_gradient": {"low": "#FCE5AB", "high": "#F8961D"},
    "value_gradient": {"low": "#4A3728", "high": "#2196F3"},
    "metric_gradient": {"low": "#9E9E9E", "high": "#2196F3"},
    "confidence_gradient": {"low": "#F44336", "high": "#2196F3"},
}

_GRADIENT_CONFIG_KEYS: dict[str, str] = {
    "relevance": "relevance_gradient",
    "value": "value_gradient",
    "metric": "metric_gradient",
    "confidence": "confidence_gradient",
}

GradientKind = Literal["relevance", "value", "metric", "confidence"]

# Backward-compatible aliases (graph heatmap).
HEATMAP_COLOR_LOW = _DEFAULT_GRADIENTS["relevance_gradient"]["low"]
HEATMAP_COLOR_HIGH = _DEFAULT_GRADIENTS["relevance_gradient"]["high"]


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def _rgb_to_hex(red: int, green: int, blue: int) -> str:
    return f"#{red:02X}{green:02X}{blue:02X}"


def _interpolate_hex(low_hex: str, high_hex: str, normalized: float) -> str:
    clamped = max(0.0, min(float(normalized), 1.0))
    low = _hex_to_rgb(low_hex)
    high = _hex_to_rgb(high_hex)
    red = int(low[0] + (high[0] - low[0]) * clamped)
    green = int(low[1] + (high[1] - low[1]) * clamped)
    blue = int(low[2] + (high[2] - low[2]) * clamped)
    return _rgb_to_hex(red, green, blue)


@lru_cache(maxsize=None)
def _gradient_endpoints(kind: GradientKind) -> tuple[str, str]:
    config_key = _GRADIENT_CONFIG_KEYS[kind]
    defaults = _DEFAULT_GRADIENTS[config_key]
    try:
        root = resolve_repo_root()
        path = root / CONFIG_REL_PATH
        if path.is_file():
            payload = json.loads(path.read_text(encoding="utf-8"))
            section = payload.get(config_key, {})
            low = section.get("low", defaults["low"])
            high = section.get("high", defaults["high"])
            return str(low), str(high)
    except Exception:
        pass
    return defaults["low"], defaults["high"]


def gradient_color(kind: GradientKind, normalized: float) -> str:
    """Map 0–1 to a configured two-stop gradient."""
    low, high = _gradient_endpoints(kind)
    return _interpolate_hex(low, high, normalized)


def relevance_gradient_color(normalized: float) -> str:
    """Cream (low) → orange (high) — Grafo heatmap and VS activity fill."""
    return gradient_color("relevance", normalized)


def value_gradient_color(normalized: float) -> str:
    """Brown (low) → blue (high) — Valor interno (V) scatter."""
    return gradient_color("value", normalized)


def metric_gradient_color(normalized: float) -> str:
    """Gray (low) → blue (high) — reserved for future plots."""
    return gradient_color("metric", normalized)


def confidence_gradient_color(normalized: float) -> str:
    """Red (low) → blue (high) — existence confidence in AI-enhanced scenarios."""
    return gradient_color("confidence", normalized)


# Alias kept for graph heatmap call sites.
relevance_heatmap_color = relevance_gradient_color
