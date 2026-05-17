from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .config import FIGURES_DIR, PROCESSED_DIR, RAW_DIR

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 13,
    "axes.labelsize": 10,
    "figure.dpi": 160,
})

BRAND = "#2F4858"
ACCENT = "#00A6A6"
SECOND = "#F6AE2D"
LIGHT = "#E8F1F2"
DARK = "#1B1B1E"
PURPLE = "#6F2DBD"


def _save(fig: plt.Figure, filename: str, figures_dir: Path = FIGURES_DIR) -> Path:
    figures_dir.mkdir(parents=True, exist_ok=True)
    path = figures_dir / filename
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", transparent=False)
    plt.close(fig)
    return path


def plot_tourism_contribution(raw_dir: Path = RAW_DIR) -> Path:
    df = pd.read_csv(raw_dir / "official_tourism_metrics.csv")
    contribution = df.query("metric == 'tourism_economy_contribution'").copy()
    visitors = df.query("metric == 'visitor_trips' and segment == 'total'").copy()

    fig, ax1 = plt.subplots(figsize=(9, 4.7))
    ax1.plot(contribution["year"], contribution["value"], marker="o", linewidth=2.5, color=BRAND)
    ax1.fill_between(contribution["year"], contribution["value"], color=LIGHT, alpha=0.85)
    ax1.set_title("Экономический масштаб туризма Санкт-Петербурга")
    ax1.set_ylabel("Вклад / потребление, млрд ₽")
    ax1.set_xlabel("Год")
    ax1.grid(axis="y", alpha=0.25)
    for x, y in zip(contribution["year"], contribution["value"]):
        ax1.text(x, y + 18, f"{y:.1f}", ha="center", color=BRAND, fontweight="bold")

    ax2 = ax1.twinx()
    ax2.plot(visitors["year"], visitors["value"], marker="s", linewidth=2.0, color=SECOND)
    ax2.set_ylabel("Туристические поездки, млн")
    for x, y in zip(visitors["year"], visitors["value"]):
        ax2.text(x, y + 0.18, f"{y:.1f}", ha="center", color=SECOND, fontweight="bold")

    ax1.text(0.01, -0.22, "Источники: Турбарометр СПб 2024; Администрация СПб, 2025", transform=ax1.transAxes, fontsize=8, color="#555")
    return _save(fig, "tourism_contribution.png")


def plot_trip_purposes(raw_dir: Path = RAW_DIR) -> Path:
    df = pd.read_csv(raw_dir / "target_audience_metrics.csv")
    purposes = df.query("metric == 'trip_purpose_share' and year == 2024").copy()
    label_map = {
        "cultural_cognitive": "Культурно-\nпознавательный",
        "visit_friends_relatives": "Друзья/\nродственники",
        "business": "Деловой",
        "event": "Событийный",
        "medical": "Медицинский",
        "education": "Образовательный",
        "other": "Прочее",
    }
    purposes["label"] = purposes["segment"].map(label_map)
    purposes = purposes.sort_values("value", ascending=True)

    fig, ax = plt.subplots(figsize=(8.5, 4.7))
    ax.barh(purposes["label"], purposes["value"], color=ACCENT)
    ax.set_title("Зачем туристы из регионов едут в Петербург, 2024")
    ax.set_xlabel("Доля, %")
    ax.grid(axis="x", alpha=0.25)
    for y, value in enumerate(purposes["value"]):
        ax.text(value + 0.7, y, f"{value:.1f}%", va="center", fontweight="bold", color=DARK)
    ax.text(0.01, -0.19, "Источник: Туризм Санкт-Петербурга. Итоги 2024 года", transform=ax.transAxes, fontsize=8, color="#555")
    return _save(fig, "trip_purposes_2024.png")


def plot_partner_market(raw_dir: Path = RAW_DIR) -> Path:
    df = pd.read_csv(raw_dir / "directory_counts.csv")
    selected = df[df["category"].isin(["restaurants_query", "hotels_query", "coffee_shops", "fast_food", "coffee_points", "canteens", "pastry_cafes"])]
    label_map = {
        "restaurants_query": "Рестораны",
        "hotels_query": "Гостиницы/отели",
        "coffee_shops": "Кофейни",
        "fast_food": "Быстрое питание",
        "coffee_points": "Точки кофе",
        "canteens": "Столовые",
        "pastry_cafes": "Кафе-кондитерские",
    }
    selected = selected.assign(label=selected["category"].map(label_map)).sort_values("count", ascending=True)

    fig, ax = plt.subplots(figsize=(8.5, 4.7))
    ax.barh(selected["label"], selected["count"], color=PURPLE)
    ax.set_title("B2B-база для рекламы и купонов в Санкт-Петербурге")
    ax.set_xlabel("Количество организаций / мест по 2GIS")
    ax.grid(axis="x", alpha=0.25)
    for y, value in enumerate(selected["count"]):
        ax.text(value + 80, y, f"{int(value):,}".replace(",", " "), va="center", fontweight="bold", color=DARK)
    ax.text(0.01, -0.19, "Источник: статический парсинг страниц 2GIS", transform=ax.transAxes, fontsize=8, color="#555")
    return _save(fig, "partner_market_2gis.png")


def plot_launch_scores(processed_dir: Path = PROCESSED_DIR) -> Path:
    df = pd.read_csv(processed_dir / "launch_zone_scores.csv").sort_values("score", ascending=True)

    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.barh(df["zone"], df["score"], color=BRAND)
    ax.set_title("Скоринг зон запуска: где ставить первую точку")
    ax.set_xlabel("Взвешенный балл из 5")
    ax.set_xlim(0, 5)
    ax.grid(axis="x", alpha=0.25)
    for y, value in enumerate(df["score"]):
        ax.text(value + 0.06, y, f"{value:.2f}", va="center", fontweight="bold", color=DARK)
    ax.text(0.01, -0.16, "Шкала основана на экспертном скоринге: трафик, исторический контекст, партнеры, операционность, погода", transform=ax.transAxes, fontsize=8, color="#555")
    return _save(fig, "launch_zone_scores.png")


def plot_unit_economics(processed_dir: Path = PROCESSED_DIR) -> Path:
    df = pd.read_csv(processed_dir / "unit_economics.csv")
    scenarios = df["scenario"]
    profit = df["monthly_profit_before_tax"] / 1000
    revenue = (df["monthly_print_revenue"] + df["monthly_ad_revenue"]) / 1000

    fig, ax = plt.subplots(figsize=(8.5, 4.7))
    ax.bar(scenarios, revenue, label="Выручка", color=LIGHT, edgecolor=BRAND)
    ax.plot(scenarios, profit, marker="o", linewidth=2.5, label="Прибыль до налога", color=BRAND)
    ax.set_title("Юнит-экономика одной точки: сценарии")
    ax.set_ylabel("тыс. ₽ в месяц")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    for x, y in zip(scenarios, profit):
        ax.text(x, y + 25, f"{y:.0f}", ha="center", fontweight="bold", color=BRAND)
    ax.text(0.01, -0.18, "Параметры — модельные допущения, проверяются на пилоте", transform=ax.transAxes, fontsize=8, color="#555")
    return _save(fig, "unit_economics.png")


def plot_breakeven(processed_dir: Path = PROCESSED_DIR) -> Path:
    df = pd.read_csv(processed_dir / "unit_economics.csv")
    fig, ax = plt.subplots(figsize=(8.5, 4.7))
    ax.bar(df["scenario"], df["breakeven_daily_prints"], color=SECOND)
    ax.set_title("Минимальная дневная продажа для безубыточности")
    ax.set_ylabel("отпечатков в день")
    ax.grid(axis="y", alpha=0.25)
    for x, y in zip(df["scenario"], df["breakeven_daily_prints"]):
        ax.text(x, y + 0.8, f"{y:.1f}", ha="center", fontweight="bold", color=DARK)
    ax.text(0.01, -0.18, "Расчет: (фиксированные затраты - рекламная выручка) / маржа печати", transform=ax.transAxes, fontsize=8, color="#555")
    return _save(fig, "breakeven_daily_prints.png")


def build_all_figures() -> list[Path]:
    return [
        plot_tourism_contribution(),
        plot_trip_purposes(),
        plot_partner_market(),
        plot_launch_scores(),
        plot_unit_economics(),
        plot_breakeven(),
    ]
