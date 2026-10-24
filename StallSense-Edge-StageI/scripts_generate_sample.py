"""Recreate reproducible SYNTHETIC data; for technical demonstration only."""
from pathlib import Path
import numpy as np
import pandas as pd

rng = np.random.default_rng(20261013)
records = []
for product, mean_demand, cost, price in [
    ("Leafy greens", 31., 25., 37.),
    ("Cabbage", 25., 20., 36.),
    ("Tomatoes", 26., 24., 44.),
]:
    for index, day in enumerate(pd.date_range("2026-04-01", "2026-10-12", freq="D")):
        weekend = day.dayofweek in (5,6)
        holiday = int((day.month, day.day) in {(4,4),(5,1),(6,19),(9,25),(10,10)})
        rain_probability = float(rng.uniform(.05,.9))
        high_temp_prediction = float(np.clip(28 + 5*np.sin(2*np.pi*index/185)+rng.normal(0,2),19,37))
        retail = max(cost+2, price + rng.choice([-2,0,0,0,2]))
        # Latent demand exists ONLY because these are synthetic observations.
        # Rain probability is a simulated PREVIOUS-DAY FORECAST, not realized weather.
        expected = (mean_demand + (5 if weekend else 0) + (9 if holiday else 0)
                    - 11*rain_probability - .4*max(0, high_temp_prediction-30)
                    - .8*(retail-price) + 2*np.sin(index/12))
        actual_demand = int(max(1, np.rint(expected + rng.normal(0,5))))
        historical_order = max(1, int(np.rint(mean_demand - 1 + rng.normal(0,7))))
        quantity_sold = min(actual_demand,historical_order)
        records.append({
            "date":day.strftime("%Y-%m-%d"),"product":product,"unit":"jin",
            "forecast_rain_probability":round(rain_probability,4),
            "forecast_high_temp":round(high_temp_prediction,1),
            "is_holiday":holiday,"retail_price":float(retail),
            "unit_cost":float(cost),"salvage_value":0.,
            "quantity_ordered":historical_order,"quantity_sold":quantity_sold,
            "left_over":max(0,historical_order-quantity_sold),
            "stockout":int(actual_demand > historical_order),
            "true_demand":actual_demand,
            "source":"SYNTHETIC_EXAMPLE_NOT_VENDOR_DATA",
        })
out = Path(__file__).parent / "data" / "synthetic_sales.csv"
pd.DataFrame(records).to_csv(out,index=False)
print(f"Generated {len(records)} demo rows at {out}")
