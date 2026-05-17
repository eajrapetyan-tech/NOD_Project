from save_history.models import UnitEconomicsScenario


def test_unit_economics_positive_base_profit():
    scenario = UnitEconomicsScenario("base", 590, 45, 5, 12_000, 125, 380_000, 520_000)
    assert scenario.monthly_print_revenue == 796_500
    assert scenario.monthly_ad_revenue == 60_000
    assert scenario.monthly_variable_cost == 168_750
    assert scenario.monthly_profit_before_tax == 307_750
    assert round(scenario.breakeven_daily_prints, 1) == 22.9


def test_no_payback_when_loss():
    scenario = UnitEconomicsScenario("bad", 200, 10, 0, 0, 250, 100_000, 500_000)
    assert scenario.payback_months is None
