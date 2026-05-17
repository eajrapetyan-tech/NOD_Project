from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SourceConfig:
    source_id: str
    title: str
    url: str
    method: str
    used_for: str


@dataclass(frozen=True)
class DirectoryCount:
    category: str
    count: int
    unit: str
    source_id: str
    comment: str = ""


@dataclass(frozen=True)
class Place:
    name: str
    address: str
    source_id: str
    comment: str = ""


@dataclass(frozen=True)
class UnitEconomicsScenario:
    scenario: str
    price_rub: int
    daily_prints: int
    ad_partners: int
    partner_fee_month_rub: int
    variable_cost_rub: int
    fixed_cost_month_rub: int
    capex_rub: int
    days_per_month: int = 30

    @property
    def monthly_print_revenue(self) -> int:
        return self.price_rub * self.daily_prints * self.days_per_month

    @property
    def monthly_ad_revenue(self) -> int:
        return self.ad_partners * self.partner_fee_month_rub

    @property
    def monthly_variable_cost(self) -> int:
        return self.variable_cost_rub * self.daily_prints * self.days_per_month

    @property
    def monthly_profit_before_tax(self) -> int:
        return (
            self.monthly_print_revenue
            + self.monthly_ad_revenue
            - self.monthly_variable_cost
            - self.fixed_cost_month_rub
        )

    @property
    def breakeven_daily_prints(self) -> float:
        margin = self.price_rub - self.variable_cost_rub
        if margin <= 0:
            return float("inf")
        return max(self.fixed_cost_month_rub - self.monthly_ad_revenue, 0) / margin / self.days_per_month

    @property
    def payback_months(self) -> Optional[float]:
        profit = self.monthly_profit_before_tax
        if profit <= 0:
            return None
        return self.capex_rub / profit
