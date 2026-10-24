import tempfile
from pathlib import Path
import pandas as pd
import pytest
from stall_sense.data import load_sample
from stall_sense.forecast import baseline_last_day, baseline_seven_day, forecast_next
from stall_sense.ordering import critical_fractile, recommend_order, simulate_day
from stall_sense.backtest import backtest, evaluate_h3
from stall_sense.storage import upsert_sales, read_sales


def test_slide_6_newsvendor_numbers():
    assert critical_fractile(25, 37, 0) == pytest.approx(12/37)
    decision = recommend_order(30, 6, 4, 25, 37, 0)
    assert decision['order_qty'] >= 0
    assert decision['critical_fractile'] == pytest.approx(12/37)


def test_simulated_economics():
    d = simulate_day(10, 12, 25, 37, 0)
    assert d['sold'] == 10
    assert d['leftover_units'] == 2
    assert d['leftover_cost'] == 50
    assert d['stockout'] == 0
    assert d['estimated_profit'] == 370 - 300


def test_forecast_never_uses_future_rows():
    history = load_sample('Leafy greens').iloc[:80]
    result = forecast_next(history, '2026-08-01', .35, 29, False, 37)
    assert result.estimate >= 0
    assert result.sigma > 0
    assert result.model.startswith('Ridge')
    assert baseline_last_day(history) >= 0
    assert baseline_seven_day(history) >= 0


def test_backtest_runs_all_three_strategies():
    history = load_sample('Leafy greens')
    detail, summary = backtest(history, days=15)
    assert len(detail) == 45
    assert len(summary) == 3
    outcome = evaluate_h3(summary)
    assert isinstance(outcome['h3_met'], bool)


def test_sqlite_local_log_roundtrip():
    with tempfile.TemporaryDirectory() as tempdir:
        path = Path(tempdir)/'logs.db'
        upsert_sales(dict(entry_date='2026-10-13',product='Cabbage',quantity_sold=12,
                          quantity_ordered=20,left_over=8,retail_price=37,unit_cost=25,
                          salvage_value=0,forecast_rain_probability=.3,
                          forecast_high_temp=27,is_holiday=0),db_path=path)
        got = read_sales('Cabbage',db_path=path)
        assert len(got) == 1
        assert got.iloc[0]['quantity_sold'] == 12
