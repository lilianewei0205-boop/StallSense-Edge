"""Expanding-window backtest, no access to future outcomes during decisions."""
from __future__ import annotations
import pandas as pd
from .forecast import forecast_next, baseline_last_day, baseline_seven_day, wape
from .ordering import recommend_order, simulate_day


def backtest(data: pd.DataFrame, days: int = 30, min_train: int = 45) -> tuple[pd.DataFrame, pd.DataFrame]:
    d = data.sort_values("date").reset_index(drop=True)
    needed = {"date", "true_demand", "quantity_sold", "forecast_rain_probability",
              "forecast_high_temp", "is_holiday", "retail_price", "unit_cost", "salvage_value"}
    if not needed.issubset(d.columns):
        raise ValueError("Backtesting true demand requires the complete synthetic demonstration dataset")
    if len(d) < min_train + 1:
        raise ValueError(f"Need at least {min_train + 1} observations")
    first = max(min_train, len(d) - days)
    rows = []
    for i in range(first, len(d)):
        earlier = d.iloc[:i]
        day = d.iloc[i]
        fc = forecast_next(earlier, day["date"], day["forecast_rain_probability"],
                           day["forecast_high_temp"], bool(day["is_holiday"]), day["retail_price"])
        critical_order = recommend_order(fc.estimate, fc.sigma, 0, day["unit_cost"],
                                         day["retail_price"], day["salvage_value"])["order_qty"]
        options = {
            "Yesterday's sales": round(baseline_last_day(earlier)),
            "Last 7-day average": round(baseline_seven_day(earlier)),
            "Forecast + Newsvendor": critical_order,
        }
        for strategy, quantity in options.items():
            outcome = simulate_day(float(day["true_demand"]), quantity,
                                   day["unit_cost"], day["retail_price"], day["salvage_value"])
            rows.append({
                "date": str(day["date"]), "strategy": strategy,
                "order_qty": quantity, "true_demand": float(day["true_demand"]),
                "actual_observed_sales": float(day["quantity_sold"]),
                "forecast": fc.estimate if strategy == "Forecast + Newsvendor" else float(quantity),
                **outcome,
            })
    result = pd.DataFrame(rows)
    grouped = result.groupby("strategy", sort=False)
    overview = grouped.agg(
        days=("date", "size"),
        leftover_cost=("leftover_cost", "sum"),
        stockout_days=("stockout", "sum"),
        estimated_profit=("estimated_profit", "sum"),
        average_order=("order_qty", "mean"),
    ).reset_index()
    overview["stockout_rate_pct"] = 100 * overview["stockout_days"] / overview["days"]
    return result, overview


def evaluate_h3(overview: pd.DataFrame) -> dict:
    base = overview.set_index("strategy").loc["Yesterday's sales"]
    ai = overview.set_index("strategy").loc["Forecast + Newsvendor"]
    return {
        "leftover_cost_reduced": bool(ai["leftover_cost"] < base["leftover_cost"]),
        "stockout_not_increased": bool(ai["stockout_rate_pct"] <= base["stockout_rate_pct"]),
        "h3_met": bool(ai["leftover_cost"] < base["leftover_cost"] and
                       ai["stockout_rate_pct"] <= base["stockout_rate_pct"]),
    }
