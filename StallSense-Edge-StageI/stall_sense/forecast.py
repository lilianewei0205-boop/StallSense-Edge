"""Leakage-aware next-day forecasting.

Important: a demand estimate from sales is potentially biased downward on stockout days.
This Stage I prototype must not be interpreted as a validated forecast of latent demand.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

FEATURES = [
    "sin_weekday", "cos_weekday", "is_holiday", "forecast_rain_probability",
    "forecast_high_temp", "retail_price", "lag1", "avg7",
]

@dataclass(frozen=True)
class ForecastResult:
    estimate: float
    sigma: float
    model: str
    samples: int
    note: str


def build_features(history: pd.DataFrame) -> pd.DataFrame:
    """Create training features using only information available before each day's sale."""
    d = history.sort_values("date").copy()
    d["date"] = pd.to_datetime(d["date"])
    d["weekday"] = d["date"].dt.dayofweek
    d["sin_weekday"] = np.sin(2 * np.pi * d["weekday"] / 7)
    d["cos_weekday"] = np.cos(2 * np.pi * d["weekday"] / 7)
    d["lag1"] = d["quantity_sold"].shift(1)
    d["avg7"] = d["quantity_sold"].shift(1).rolling(7, min_periods=7).mean()
    return d


def baseline_last_day(history: pd.DataFrame) -> float:
    if history.empty:
        return 0.0
    return float(history.sort_values("date").iloc[-1]["quantity_sold"])


def baseline_seven_day(history: pd.DataFrame) -> float:
    if history.empty:
        return 0.0
    return float(history.sort_values("date").tail(7)["quantity_sold"].mean())


def forecast_next(
    history: pd.DataFrame,
    date,
    rain_probability: float,
    high_temp: float,
    is_holiday: bool,
    retail_price: float,
) -> ForecastResult:
    """Fit a small ridge model if enough observations exist; otherwise use rolling mean.

    Future inputs must be forecasts or facts known at ordering time. The feature
    named `forecast_rain_probability` in the sample file represents a forecast,
    not realized future rainfall.
    """
    history = history.sort_values("date").copy()
    if len(history) == 0:
        return ForecastResult(0, 1, "No-data placeholder", 0,
                              "Please enter sales history before using this forecast.")
    baseline = baseline_seven_day(history)
    obs = history["quantity_sold"].to_numpy(dtype=float)
    historical_sigma = max(1.0, float(np.std(obs[-min(28, len(obs)):], ddof=1)) if len(obs) > 1 else baseline * .2)
    if len(history) < 30:
        return ForecastResult(max(0., baseline), historical_sigma, "7-day rolling average", len(history),
                              "Fewer than 30 records: using a simple baseline, not an ML model.")

    train = build_features(history).dropna(subset=FEATURES + ["quantity_sold"])
    if len(train) < 20:
        return ForecastResult(max(0., baseline), historical_sigma, "7-day rolling average", len(history),
                              "Insufficient complete training features; using baseline.")

    t = pd.Timestamp(date)
    weekday = int(t.dayofweek)
    row = pd.DataFrame([{
        "sin_weekday": math.sin(2 * math.pi * weekday / 7),
        "cos_weekday": math.cos(2 * math.pi * weekday / 7),
        "is_holiday": int(is_holiday),
        "forecast_rain_probability": float(rain_probability),
        "forecast_high_temp": float(high_temp),
        "retail_price": float(retail_price),
        "lag1": baseline_last_day(history),
        "avg7": baseline,
    }])
    model = make_pipeline(StandardScaler(), Ridge(alpha=12.0))
    model.fit(train[FEATURES].astype(float), train["quantity_sold"].astype(float))
    prediction = max(0.0, float(model.predict(row[FEATURES])[0]))
    residuals = train["quantity_sold"].to_numpy(float) - model.predict(train[FEATURES])
    sigma = max(1.0, float(np.std(residuals, ddof=1)))
    return ForecastResult(prediction, sigma, "Ridge regression (Stage I)", len(history),
                          "Uncertainty is a rough residual estimate, not a calibrated prediction interval.")


def wape(actual: list[float], predicted: list[float]) -> float | None:
    a = np.asarray(actual, dtype=float)
    p = np.asarray(predicted, dtype=float)
    if len(a) == 0 or float(np.sum(np.abs(a))) == 0:
        return None
    return float(100 * np.sum(np.abs(a - p)) / np.sum(np.abs(a)))
