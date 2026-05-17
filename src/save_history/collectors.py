from __future__ import annotations

import re
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests
from bs4 import BeautifulSoup

from .config import DEFAULT_HEADERS, HTML_SNAPSHOT_DIR, RAW_DIR
from .models import DirectoryCount, Place


class BaseCollector(ABC):
    source_id: str

    @abstractmethod
    def collect(self) -> pd.DataFrame:
        raise NotImplementedError


class HttpClient:
    def __init__(self, timeout: int = 20, retries: int = 2, pause: float = 1.0):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.timeout = timeout
        self.retries = retries
        self.pause = pause

    def get_text(self, url: str) -> str:
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                response.encoding = response.apparent_encoding or response.encoding
                return response.text
            except Exception as exc:
                last_error = exc
                if attempt < self.retries:
                    time.sleep(self.pause)
        raise RuntimeError(f"Failed to fetch {url}: {last_error}")


class HtmlSource:
    def __init__(self, url: str, snapshot_name: str | None = None, offline: bool = True):
        self.url = url
        self.snapshot_name = snapshot_name
        self.offline = offline
        self.client = HttpClient()

    def read(self) -> str:
        if self.offline:
            if not self.snapshot_name:
                raise ValueError("offline=True requires snapshot_name")
            path = HTML_SNAPSHOT_DIR / self.snapshot_name
            return path.read_text(encoding="utf-8")
        return self.client.get_text(self.url)


class TwoGisCountCollector(BaseCollector):
    def __init__(self, source_id: str, url: str, snapshot_name: str, category_name: str, offline: bool = True):
        self.source_id = source_id
        self.url = url
        self.snapshot_name = snapshot_name
        self.category_name = category_name
        self.offline = offline

    def collect(self) -> pd.DataFrame:
        html = HtmlSource(self.url, self.snapshot_name, self.offline).read()
        soup = BeautifulSoup(html, "lxml")
        text = " ".join(soup.get_text(" ", strip=True).split())
        count = self._extract_places_count(text)
        rows = [DirectoryCount(self.category_name, count, "places", self.source_id).__dict__]
        return pd.DataFrame(rows)

    @staticmethod
    def _extract_places_count(text: str) -> int:
        match = re.search(r"Места\s+(\d[\d\s]*)", text)
        if not match:
            raise ValueError("Could not find `Места N` pattern in 2GIS HTML")
        return int(match.group(1).replace(" ", ""))


class TwoGisFoodRubricsCollector(BaseCollector):
    source_id = "two_gis_food_rubrics"

    def __init__(self, url: str, snapshot_name: str = "2gis_food_rubrics.html", offline: bool = True):
        self.url = url
        self.snapshot_name = snapshot_name
        self.offline = offline

    def collect(self) -> pd.DataFrame:
        html = HtmlSource(self.url, self.snapshot_name, self.offline).read()
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text("\n", strip=True)
        pairs = self._extract_pairs(text.splitlines())
        rows = [DirectoryCount(category, count, "organizations", self.source_id).__dict__ for category, count in pairs]
        return pd.DataFrame(rows)

    @staticmethod
    def _extract_pairs(lines: Iterable[str]) -> list[tuple[str, int]]:
        cleaned = [line.strip() for line in lines if line.strip()]
        pairs: list[tuple[str, int]] = []
        for idx, line in enumerate(cleaned[:-1]):
            next_line = cleaned[idx + 1]
            match = re.match(r"^(\d[\d\s]*)\s+организац", next_line)
            if match and not line[0].isdigit():
                pairs.append((line, int(match.group(1).replace(" ", ""))))
        return pairs


class VisitPetersburgPlacesCollector(BaseCollector):
    source_id = "visit_petersburg_places"

    ADDRESS_MARKERS = (" о-в", "пр.", "пл.", "наб.", "ул.")

    def __init__(self, url: str, snapshot_name: str = "visit_petersburg_places.html", offline: bool = True):
        self.url = url
        self.snapshot_name = snapshot_name
        self.offline = offline

    def collect(self) -> pd.DataFrame:
        html = HtmlSource(self.url, self.snapshot_name, self.offline).read()
        soup = BeautifulSoup(html, "lxml")
        candidates = [a.get_text(" ", strip=True) for a in soup.find_all("a")]
        rows = []
        for item in candidates:
            parsed = self._split_name_address(item)
            if parsed is not None:
                rows.append(Place(parsed[0], parsed[1], self.source_id, "official tourist portal").__dict__)
        return pd.DataFrame(rows).drop_duplicates()

    @classmethod
    def _split_name_address(cls, text: str) -> tuple[str, str] | None:
        if len(text) < 8:
            return None
        marker_positions = [text.find(marker) for marker in cls.ADDRESS_MARKERS if marker in text]
        if not marker_positions:
            return None
        pos = min(marker_positions)
        before = text[:pos].rstrip()
        after = text[pos:].lstrip()
        words = before.split()
        if not words:
            return None
        street_word = words[-1]
        name = " ".join(words[:-1]).strip()
        address = f"{street_word} {after}".strip()
        if not name:
            return None
        return name, address


def collect_all(offline: bool = True) -> dict[str, pd.DataFrame]:
    collectors: list[BaseCollector] = [
        TwoGisCountCollector(
            source_id="two_gis_restaurants",
            url="https://2gis.ru/spb/search/Рестораны%20СПб%20(Санкт-Петербурга)",
            snapshot_name="2gis_restaurants.html",
            category_name="restaurants_query",
            offline=offline,
        ),
        TwoGisCountCollector(
            source_id="two_gis_hotels",
            url="https://2gis.ru/spb/search/Гостиницы%20(отели)/rubricId/269",
            snapshot_name="2gis_hotels.html",
            category_name="hotels_query",
            offline=offline,
        ),
        TwoGisFoodRubricsCollector(
            url="https://2gis.ru/spb/rubrics/subrubrics/111546",
            offline=offline,
        ),
        VisitPetersburgPlacesCollector(
            url="https://visit-petersburg.ru/leisure/places/",
            offline=offline,
        ),
    ]
    return {collector.source_id: collector.collect() for collector in collectors}


def save_collected_frames(frames: dict[str, pd.DataFrame], raw_dir: Path = RAW_DIR) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True)
    for source_id, frame in frames.items():
        frame.to_csv(raw_dir / f"{source_id}_parsed.csv", index=False)
