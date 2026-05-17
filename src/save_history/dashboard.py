from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def create_app() -> Dash:
    official = pd.read_csv(RAW_DIR / "official_tourism_metrics.csv")
    directory = pd.read_csv(RAW_DIR / "directory_counts.csv")
    zones = pd.read_csv(PROCESSED_DIR / "launch_zone_scores.csv")
    economics = pd.read_csv(PROCESSED_DIR / "unit_economics.csv")

    contribution = official.query("metric == 'tourism_economy_contribution'")
    partner_categories = directory[directory["category"].isin([
        "restaurants_query", "hotels_query", "coffee_shops", "fast_food", "coffee_points"
    ])]

    app = Dash(__name__)
    app.title = "Save you in history — research dashboard"
    app.layout = html.Div(
        style={"fontFamily": "Arial, sans-serif", "margin": "32px", "maxWidth": "1160px"},
        children=[
            html.H1("Save you in history: исследование запуска"),
            html.P(
                "Дашборд показывает рыночные индикаторы, партнерскую базу, скоринг географии и юнит-экономику. "
                "Данные лежат в data/raw и data/processed."
            ),
            dcc.Graph(
                figure=px.line(
                    contribution,
                    x="year",
                    y="value",
                    markers=True,
                    title="Туристско-экскурсионное потребление / вклад в экономику СПб",
                    labels={"year": "Год", "value": "млрд ₽"},
                )
            ),
            dcc.Graph(
                figure=px.bar(
                    partner_categories.sort_values("count"),
                    x="count",
                    y="category",
                    orientation="h",
                    title="B2B-партнерская база по 2GIS",
                    labels={"count": "Количество", "category": "Категория"},
                )
            ),
            dcc.Graph(
                figure=px.bar(
                    zones.sort_values("score"),
                    x="score",
                    y="zone",
                    orientation="h",
                    title="Скоринг зон запуска",
                    labels={"score": "Балл", "zone": "Зона"},
                    hover_data=["reason"],
                )
            ),
            dcc.Graph(
                figure=px.bar(
                    economics,
                    x="scenario",
                    y="monthly_profit_before_tax",
                    title="Прибыль одной точки до налога по сценариям",
                    labels={"scenario": "Сценарий", "monthly_profit_before_tax": "₽ / месяц"},
                )
            ),
        ],
    )
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
