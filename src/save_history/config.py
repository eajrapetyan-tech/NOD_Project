from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
FIGURES_DIR = PROJECT_ROOT / "figures"
REPORTS_DIR = PROJECT_ROOT / "reports"
HTML_SNAPSHOT_DIR = RAW_DIR / "html_snapshots"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; HSE-NES-Data-Science-Project/1.0; "
        "research-only; contact: eajrapetyan-tech)"
    )
}
