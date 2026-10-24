"""Local-only SQLite bookkeeping, with no network access or cloud upload."""
import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "local_stallsense.db"


def connect(db_path=DB_PATH):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db_path))
    con.execute("""CREATE TABLE IF NOT EXISTS sales_logs (
      entry_date TEXT NOT NULL,
      product TEXT NOT NULL,
      quantity_sold REAL NOT NULL,
      quantity_ordered REAL NOT NULL,
      left_over REAL NOT NULL,
      retail_price REAL NOT NULL,
      unit_cost REAL NOT NULL,
      salvage_value REAL NOT NULL,
      forecast_rain_probability REAL NOT NULL,
      forecast_high_temp REAL NOT NULL,
      is_holiday INTEGER NOT NULL,
      PRIMARY KEY (entry_date, product)
    )""")
    con.commit()
    return con


def upsert_sales(record: dict, db_path=DB_PATH):
    keys = ["entry_date", "product", "quantity_sold", "quantity_ordered", "left_over",
            "retail_price", "unit_cost", "salvage_value", "forecast_rain_probability",
            "forecast_high_temp", "is_holiday"]
    with connect(db_path) as con:
        con.execute(f"INSERT OR REPLACE INTO sales_logs ({','.join(keys)}) VALUES ({','.join(['?'] * len(keys))})",
                    tuple(record[k] for k in keys))
        con.commit()


def read_sales(product: str, db_path=DB_PATH) -> pd.DataFrame:
    with connect(db_path) as con:
        d = pd.read_sql_query("SELECT * FROM sales_logs WHERE product = ? ORDER BY entry_date",
                              con, params=(product,))
    if len(d):
        d = d.rename(columns={"entry_date": "date"})
    return d
