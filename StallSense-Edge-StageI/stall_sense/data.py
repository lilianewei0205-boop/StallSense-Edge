"""Demo data loading. No real merchant transactions are bundled."""
from pathlib import Path
import pandas as pd

SAMPLE_CSV = Path(__file__).resolve().parents[1] / "data" / "synthetic_sales.csv"


def load_sample(product: str | None = None) -> pd.DataFrame:
    data = pd.read_csv(SAMPLE_CSV, parse_dates=["date"])
    if product:
        data = data[data["product"] == product]
    return data.sort_values("date").reset_index(drop=True)
