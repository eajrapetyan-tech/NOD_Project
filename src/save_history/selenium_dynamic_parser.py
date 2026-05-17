from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class DynamicCard:
    name: str
    rating: str
    address: str


def parse_2gis_cards_dynamic(url: str, limit: int = 20) -> list[DynamicCard]:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1440,1000")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        cards = driver.find_elements(By.CSS_SELECTOR, "article, div")
        parsed: list[DynamicCard] = []
        for card in cards:
            text = " ".join(card.text.split())
            if not text or "оцен" not in text.lower():
                continue
            pieces = text.split(" ")
            name = " ".join(pieces[:6])[:80]
            rating = next((p for p in pieces if p.replace(".", "", 1).isdigit() and len(p) <= 3), "")
            address = text[:180]
            parsed.append(DynamicCard(name=name, rating=rating, address=address))
            if len(parsed) >= limit:
                break
        return parsed
    finally:
        driver.quit()


def cards_to_rows(cards: Iterable[DynamicCard]) -> list[dict[str, str]]:
    return [card.__dict__ for card in cards]
