from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

from .config import PROCESSED_DIR, RAW_DIR
from .models import UnitEconomicsScenario


WEIGHTS = {
    "foot_traffic": 0.28,
    "historical_fit": 0.22,
    "partner_density": 0.22,
    "operations": 0.16,
    "weather_resilience": 0.12,
}


def read_raw(raw_dir: Path = RAW_DIR) -> dict[str, pd.DataFrame]:
    return {
        "official": pd.read_csv(raw_dir / "official_tourism_metrics.csv"),
        "audience": pd.read_csv(raw_dir / "target_audience_metrics.csv"),
        "directory": pd.read_csv(raw_dir / "directory_counts.csv"),
        "places": pd.read_csv(raw_dir / "visit_petersburg_places.csv"),
    }


def build_launch_zone_scores() -> pd.DataFrame:
    zones = [
        {
            "zone": "Невский проспект — Казанский собор — Дом книги",
            "main_places": "Дом книги, Казанский собор, Спас на Крови, рестораны Невского",
            "foot_traffic": 5,
            "historical_fit": 4,
            "partner_density": 5,
            "operations": 4,
            "weather_resilience": 4,
            "reason": "Самый понятный первый B2C-трафик и максимальная плотность ресторанов/кофеен.",
        },
        {
            "zone": "Дворцовая площадь — Эрмитаж — Адмиралтейство",
            "main_places": "Эрмитаж, Зимний дворец, Дворцовая площадь",
            "foot_traffic": 5,
            "historical_fit": 5,
            "partner_density": 4,
            "operations": 3,
            "weather_resilience": 3,
            "reason": "Наиболее сильный исторический образ и высокий туристический поток, но сложнее согласования.",
        },
        {
            "zone": "Исаакиевская площадь — Медный всадник",
            "main_places": "Исаакиевский собор, Сенатская площадь, Медный всадник",
            "foot_traffic": 4,
            "historical_fit": 5,
            "partner_density": 4,
            "operations": 4,
            "weather_resilience": 4,
            "reason": "Хороший баланс исторического контекста, фото-позиций и близости ресторанов/отелей.",
        },
        {
            "zone": "Петропавловская крепость",
            "main_places": "Петропавловская крепость, Заячий остров",
            "foot_traffic": 4,
            "historical_fit": 5,
            "partner_density": 3,
            "operations": 3,
            "weather_resilience": 3,
            "reason": "Сильная историческая точка, но партнерская плотность ниже, чем на Невском.",
        },
        {
            "zone": "Новая Голландия — Адмиралтейский район",
            "main_places": "Новая Голландия, Мариинский театр, Исаакиевская площадь рядом",
            "foot_traffic": 3,
            "historical_fit": 4,
            "partner_density": 4,
            "operations": 5,
            "weather_resilience": 4,
            "reason": "Более управляемая площадка для тестов и событий, но меньше классического туристического трафика.",
        },
    ]
    frame = pd.DataFrame(zones)
    frame["score"] = sum(frame[col] * weight for col, weight in WEIGHTS.items()).round(2)
    return frame.sort_values("score", ascending=False).reset_index(drop=True)


def build_unit_economics() -> pd.DataFrame:
    scenarios = [
        UnitEconomicsScenario("conservative", 590, 25, 3, 10_000, 125, 380_000, 520_000),
        UnitEconomicsScenario("base", 590, 45, 5, 12_000, 125, 380_000, 520_000),
        UnitEconomicsScenario("optimistic", 690, 75, 8, 15_000, 125, 420_000, 600_000),
    ]
    rows = []
    for scenario in scenarios:
        row = asdict(scenario)
        row.update(
            monthly_print_revenue=scenario.monthly_print_revenue,
            monthly_ad_revenue=scenario.monthly_ad_revenue,
            monthly_variable_cost=scenario.monthly_variable_cost,
            monthly_profit_before_tax=scenario.monthly_profit_before_tax,
            breakeven_daily_prints=round(scenario.breakeven_daily_prints, 1),
            payback_months=(None if scenario.payback_months is None else round(scenario.payback_months, 1)),
        )
        rows.append(row)
    return pd.DataFrame(rows)


def build_market_estimates(raw: dict[str, pd.DataFrame]) -> pd.DataFrame:
    official = raw["official"]
    trips_2025 = official.query("metric == 'visitor_trips' and year == 2025")["value"].iloc[0]
    contribution_2024 = official.query("metric == 'tourism_economy_contribution' and year == 2024")["value"].iloc[0]
    souvenir_share = official.query("metric == 'spending_share' and year == 2024 and segment == 'souvenirs'")["value"].iloc[0]

    price = 590
    rows = []
    for conversion in [0.005, 0.01, 0.02, 0.03]:
        rows.append(
            {
                "conversion_rate": conversion,
                "annual_buyers_estimate": trips_2025 * 1_000_000 * conversion,
                "annual_b2c_revenue_rub": trips_2025 * 1_000_000 * conversion * price,
                "assumed_price_rub": price,
            }
        )
    frame = pd.DataFrame(rows)
    frame["souvenir_consumption_2024_rub"] = contribution_2024 * 1_000_000_000 * souvenir_share / 100
    frame["note"] = (
        "B2C TAM is a scenario estimate, not observed demand; souvenir consumption uses official 2024 structure."
    )
    return frame


def build_marketing_plan() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "stage": "Пилот: 1 точка / 6 недель",
                "channel": "QR-купон внизу открытки + промокод партнера",
                "audience": "Турист после фото у достопримечательности",
                "budget_rub": 45_000,
                "kpi": "конверсия QR 8-12%, 5 партнеров, 1200+ отпечатков/мес.",
            },
            {
                "stage": "Пилот: 1 точка / 6 недель",
                "channel": "2GIS/Яндекс Карты: карточка точки и отзывы",
                "audience": "Турист, ищущий развлечения и сувениры рядом",
                "budget_rub": 30_000,
                "kpi": "30+ отзывов, рейтинг 4.7+, 15% продаж из поиска",
            },
            {
                "stage": "Пилот: 1 точка / 6 недель",
                "channel": "Туристские инфоцентры и стойки отелей",
                "audience": "Семейные туристы и гости из регионов",
                "budget_rub": 25_000,
                "kpi": "10 размещений листовок, 200+ переходов по QR",
            },
            {
                "stage": "Масштабирование: 3 точки",
                "channel": "VK/Telegram с геометками и UGC-механикой",
                "audience": "18-44, пары, семьи, молодые туристы",
                "budget_rub": 90_000,
                "kpi": "1000+ публикаций/отметок за сезон, CAC ниже 120 руб.",
            },
            {
                "stage": "Масштабирование: B2B",
                "channel": "Пакеты рекламы для ресторанов/отелей",
                "audience": "Локальный HoReCa-бизнес в радиусе 1-2 км",
                "budget_rub": 20_000,
                "kpi": "8 платящих партнеров на точку, 70% продлений",
            },
        ]
    )


def write_processed(output_dir: Path = PROCESSED_DIR) -> dict[str, pd.DataFrame]:
    raw = read_raw()
    output_dir.mkdir(parents=True, exist_ok=True)
    frames = {
        "launch_zone_scores": build_launch_zone_scores(),
        "unit_economics": build_unit_economics(),
        "market_estimates": build_market_estimates(raw),
        "marketing_plan": build_marketing_plan(),
    }
    for name, frame in frames.items():
        frame.to_csv(output_dir / f"{name}.csv", index=False)
    return frames


def weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    values = values.astype(float)
    weights = weights.astype(float)
    if np.isclose(weights.sum(), 0):
        return float("nan")
    return float((values * weights).sum() / weights.sum())
