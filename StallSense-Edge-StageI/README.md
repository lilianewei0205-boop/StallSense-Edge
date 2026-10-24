# 🥬 StallSense Edge

**An offline-first AI ordering advisor for traditional market vendors**  
ASUS UGen AI League Innovation Hackathon · **Stage I** · Workplace AI · Battlefield Lightning (UGen300 planned)

> **Research hypothesis H3:** Can AI-assisted purchase decisions reduce leftover inventory costs **without raising stockout risk**?

## What is implemented (Stage I)

- A working local **Streamlit web app** using large-input daily transaction recording.
- **SQLite** for storing a vendor's own records on the host machine, without uploading them to any service.
- **Demand prediction** with two transparent baselines (yesterday's sales and the preceding seven-day mean) plus a lightweight **Ridge regression** model using only information available at ordering time: weekday, holiday, previously issued rain/temperature forecast, price and lagged sales.
- **Deterministic newsvendor formula** for ordering (model estimates demand; arithmetic determines quantity).
- **Walk-forward H3 replay** comparing yesterday's-sales baseline, 7-day average, and forecast-plus-newsvendor on the same **synthetic known demand**, with leftover cost, stockout-day rate and estimated gross profit.
- Downloadable recommendation and backtest CSVs.
- Tests verifying slide 6's 25/37/0 NT$ example, ordering economics, history-only forecasting, backtest runs and SQLite writes.

## Status and scientific integrity

This project is a **functional Stage I algorithm and UX prototype**, **not** a verified AI Accelerator implementation or a real-world business-impact study.

| Feature | Status |
|---|---|
| Large-input sales logging | ✅ Implemented on laptop (local SQLite) |
| Yesterday / 7-day baselines | ✅ Implemented |
| Ridge model with external-type features | ✅ Implemented; weather is manually entered or simulated |
| Newsvendor quantity recommendation | ✅ Implemented |
| Walk-forward replay for H3 | ✅ Implemented on **synthetic data only** |
| Vendor field data & H3 validated outcome | ❌ Not yet obtained |
| Automated external APIs | ❌ Not integrated; enter weather data manually |
| UGen300/Hailo-10H visual footfall inference | 🔜 Stage II plan only |
| On-device speech / language model | 🔜 Stage II plan only |
| Power/latency/72-hour hardware metrics | ❌ Not measured |

The screenshot supplied for Stage I specifies a deadline of **October 28, 2026, 17:00** (Taiwan time). Any outdated timelines in earlier slides should be checked.

## Quick start (macOS / Windows / Linux)

Install **Python 3.10+**. Then run from the project root:

```bash
python -m venv .venv
```

Activate the environment:

```bash
# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install dependencies and launch:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Streamlit prints a local URL (typically `http://localhost:8501`). Open it in your browser.

**If the app does not start:** first check `python --version`; use `py -m ...` on Windows if `python` is not recognized. Do not upload personal vendor sales data to the repository.

## Three-minute demo storyline

1. **0:00–0:30 — Problem:** Buying too much creates leftover losses; buying too little causes lost margin. H3 is **a hypothesis**, not a proven result.
2. **0:30–1:05 — Input:** Show the large-field daily sales and purchases form. Recording works locally in SQLite. Speech is **not yet implemented**.
3. **1:05–1:50 — Prediction and order:** Select the synthetic sample, enter forecast weather and a date, view predicted sales, critical fractile, and recommended quantity.
4. **1:50–2:35 — H3 replay:** Run chronological strategy comparison and show the observed simulation output **whether or not H3 is met**. Do not claim actual merchant savings.
5. **2:35–3:00 — Stage II:** Explain planned Hailo-10H footfall and voice integration, privacy protections and benchmarks to be measured.

## How the newsvendor calculation works

The proposal's illustrative numbers are **purchase cost** NT$25/jin, **retail price** NT$37/jin, **salvage value** NT$0/jin.

- Underage (missed-margin) cost: `Cu = retail - purchase = 37 - 25 = 12`.
- Overage (leftover) cost: `Co = purchase - salvage = 25 - 0 = 25`.
- Critical fractile: `Cu / (Cu + Co) = 12 / 37 ≈ 0.324`.
- Determine a demand quantile at that service fractile, then subtract available saleable inventory to obtain the purchase quantity.

**Prototype assumptions:** Demand uncertainty is approximated with a normal distribution using a **rough in-sample residual sigma**, **not** a calibrated real-world uncertainty interval. Unit increments are 1 jin. Fresh unsold items are assumed to have a salvage value supplied by the user. Partial inventories and other constraints need field calibration.

## Correctness of the H3 replay

The `data/synthetic_sales.csv` file is **intentionally generated** with a latent `true_demand` column. In actual retail data, **sales are censored on stockout days**: you cannot observe everyone who wanted to purchase after selling out. The app intentionally **disables H3 counterfactual replay on real local logs**, rather than pretend to know unobserved demand.

For each held-out date, the model fits on **prior dates only** and uses *then-available* data. Simulated weather variables represent previously issued forecasts. All strategies face the same synthetic demand and simplified zero-carryover economics. The results cannot be used to claim validated field gains or real stockout impacts.

## Data schema

`data/synthetic_sales.csv` includes:

- `date`, `product`, `unit`
- `quantity_ordered`, `quantity_sold`, `left_over`, `stockout`
- `retail_price`, `unit_cost`, `salvage_value`
- `forecast_rain_probability`, `forecast_high_temp`, `is_holiday`
- `true_demand` **(SYNTHETIC ONLY)**

All currency is NT$ and sale quantities use **jin (斤)** in this sample. Do not mix kilograms or pieces without unit conversion.

## Run automated tests

```bash
python -m pip install pytest
python -m pytest -q
```

The app requires no API key and makes no external data calls.

## Stage II plan / ASUS UGen300

See [`docs/STAGE_II_ROADMAP.md`](docs/STAGE_II_ROADMAP.md). The **host CPU** runs tabular forecasts and ordering rules; proposed **UGen300/Hailo-10H** usage is camera-based anonymous footfall analysis and feasible local speech components, subject to actual hardware compatibility checks.

**No automatic vegetable-photo inventory recognition is implemented here:** the final proposal prioritizes large-button/voice bookkeeping and puts **footfall camera** rather than inventory scanning into Stage II.

## References and provenance

This repository is derived from the team's *StallSense Edge — ASUS UGen AI League Stage I Proposal* (17-page supplied slide PDF): solution loop pp. 5–6, architecture pp. 7–9, H3 evaluation pp. 10–11, Stage II roadmap p. 12, limitations p. 15. Any added implementation decisions (for example Ridge regression, synthetic-data generator, and local Streamlit UI) are **prototype engineering choices**, not claimed verbatim from the slide deck.

- [ASUS UGen300 product page](https://www.asus.com/motherboards-components/ai-accelerator/ugen/ugen300-usb-8g/)
- [Hailo Model Zoo](https://github.com/hailo-ai/hailo_model_zoo)
- [Taiwan Central Weather Administration data platform](https://opendata.cwa.gov.tw/)
- [Taiwan agriculture open data](https://data.moa.gov.tw/)
- Arrow, Harris & Marschak (1951), *Optimal inventory policy*, *Econometrica*.

## GitHub publication

These local files are **not yet an online repository**. Follow [`docs/GITHUB_UPLOAD.md`](docs/GITHUB_UPLOAD.md) to publish them to your GitHub account and obtain your real repository URL. Do not invent a URL before publishing.

## Ethics and limitations

This is an educational decision-support prototype, not an autonomous purchase system. Ordering remains a human decision. No faces, person-identifying photos, or actual customer transactions are bundled. Field research, stockout-demand correction, model calibration, accessibility, licensing of external datasets, and fairness across market settings remain open work.

## License

MIT — see `LICENSE`.
