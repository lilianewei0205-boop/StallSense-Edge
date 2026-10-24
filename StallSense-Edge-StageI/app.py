"""StallSense Edge | Stage I live demo. Run with: streamlit run app.py"""
from datetime import date, timedelta
from pathlib import Path
import math
import pandas as pd
import streamlit as st

from stall_sense.backtest import backtest, evaluate_h3
from stall_sense.data import load_sample
from stall_sense.forecast import baseline_last_day, baseline_seven_day, forecast_next
from stall_sense.ordering import recommend_order
from stall_sense.storage import upsert_sales, read_sales

st.set_page_config(page_title="StallSense Edge", page_icon="🥬", layout="wide")
st.markdown("""<style>
.block-container {max-width:1150px;padding-top:1.5rem}
[data-testid="stMetricValue"] {font-size:2.1rem}
</style>""", unsafe_allow_html=True)
st.title("🥬 StallSense Edge")
st.caption("Offline-first ordering advisor for traditional market vendors · Workplace AI · Stage I prototype")
st.info("**Prototype disclosure:** Sales data included in this repository are synthetic. No ASUS UGen300, video analytics, voice recognition, or vendor field validation is claimed.", icon="ℹ️")

all_samples = load_sample()
products = list(sorted(all_samples["product"].unique()))
with st.sidebar:
    st.header("Demo controls")
    source = st.radio("Data source", ["Synthetic sample", "My local logs"], help="Never mix synthetic and real transaction records in a model.")
    product = st.selectbox("Product", products)
    label_unit = "jin (斤)"
    st.caption("This demonstration uses jin (斤) as the inventory unit. The unit must match throughout.")
    st.divider()
    st.markdown("**Stage I:** CPU forecasting + newspaper-vendor formula + evaluation")
    st.markdown("**Stage II (planned):** UGen300 footfall detection, local speech, and real-hardware tests")

history = load_sample(product) if source == "Synthetic sample" else read_sales(product)
if not history.empty:
    history["date"] = pd.to_datetime(history["date"])
    recent = history.sort_values("date").iloc[-1]
    suggested_cost = float(recent["unit_cost"])
    suggested_price = float(recent["retail_price"])
    suggested_salvage = float(recent["salvage_value"])
    last_date = history["date"].max().date()
else:
    suggested_cost, suggested_price, suggested_salvage = 25., 37., 0.
    last_date = date.today() - timedelta(days=1)

record_tab, advise_tab, backtest_tab, roadmap_tab = st.tabs([
    "📝 1. Daily log", "📈 2. Tomorrow's order", "🧪 3. H3 backtest", "🧩 4. Architecture"
])

with record_tab:
    st.subheader("Record today's inventory and sales")
    st.write("Large-input bookkeeping for a busy vendor. Speech recognition is planned for Stage II, not implemented here.")
    with st.form("daily_record"):
        c1,c2,c3 = st.columns(3)
        entry_date = c1.date_input("Date", date.today())
        sold = c2.number_input(f"Quantity sold ({label_unit})", min_value=0., value=20., step=1.)
        ordered = c3.number_input(f"Quantity received ({label_unit})", min_value=0., value=28., step=1.)
        c4,c5,c6 = st.columns(3)
        price = c4.number_input("Retail price (NT$/jin)", min_value=0., value=suggested_price, step=1.)
        cost = c5.number_input("Purchase cost (NT$/jin)", min_value=0., value=suggested_cost, step=1.)
        salvage = c6.number_input("Salvage value (NT$/jin)", min_value=0., max_value=cost, value=min(suggested_salvage,cost), step=1.)
        st.markdown("**Forecast information available before today's sales**")
        c7,c8,c9 = st.columns(3)
        expected_rain = c7.slider("Earlier forecast: rain probability (%)",0,100,30,5)
        expected_temp = c8.number_input("Earlier forecast: high temperature (°C)",value=27.,step=1.)
        holiday = c9.checkbox("Holiday")
        leave = max(0., ordered - sold)
        st.caption(f"Calculated unsold inventory: {leave:.1f} {label_unit}. For carrying stock into tomorrow, manually check whether it is still saleable.")
        save = st.form_submit_button("Save locally (SQLite)", type="primary")
        if save:
            if sold > ordered:
                st.error("Quantity sold cannot exceed today's received quantity in this simplified daily form.")
            else:
                upsert_sales({"entry_date":str(entry_date),"product":product,
                              "quantity_sold":sold,"quantity_ordered":ordered,
                              "left_over":leave,"retail_price":price,"unit_cost":cost,
                              "salvage_value":salvage,"forecast_rain_probability":expected_rain/100,
                              "forecast_high_temp":expected_temp,"is_holiday":int(holiday)})
                st.success("Saved to data/local_stallsense.db on this computer. Reload the app to update your local forecasting history.")
    if source == "My local logs" and len(history):
        st.caption(f"Your local dataset contains {len(history)} records for {product}; no data is transmitted.")
        st.dataframe(history.tail(8), hide_index=True, use_container_width=True)

with advise_tab:
    st.subheader("How much should I order tomorrow?")
    with st.container(border=True):
        c1,c2,c3 = st.columns(3)
        next_day = c1.date_input("Ordering for", value=max(date.today()+timedelta(days=1),last_date+timedelta(days=1)), min_value=last_date+timedelta(days=1), key="next_day")
        tomorrow_rain = c2.slider("Tomorrow's rain forecast (%)",0,100,30,5)/100.
        tomorrow_temp = c3.number_input("Tomorrow's predicted high (°C)",value=27.,step=1.)
        c4,c5 = st.columns(2)
        holiday_next = c4.checkbox("Tomorrow is a holiday",value=False)
        available_inventory = c5.number_input(f"Saleable carry-over ({label_unit})",min_value=0.,value=3.,step=1.)
        p1,p2,p3 = st.columns(3)
        unit_cost = p1.number_input("Purchase cost (NT$/jin)",min_value=0.,value=suggested_cost,step=1.,key="order_cost")
        unit_price = p2.number_input("Retail price (NT$/jin)",min_value=0.,value=suggested_price,step=1.,key="order_price")
        salvage_value = p3.number_input("Unsold salvage (NT$/jin)",min_value=0.,max_value=unit_cost,value=min(suggested_salvage,unit_cost),step=1.,key="order_salvage")
    if history.empty:
        st.warning("No local sales records yet. Use the synthetic sample, or enter records in the Daily log tab.")
    else:
        result = forecast_next(history, next_day, tomorrow_rain, tomorrow_temp, holiday_next, unit_price)
        rec = recommend_order(result.estimate,result.sigma,available_inventory,unit_cost,unit_price,salvage_value)
        m1,m2,m3 = st.columns(3)
        m1.metric("Predicted daily sales",f"{result.estimate:.1f} jin",help="This estimates observed sales, not necessarily all unmet demand.")
        m2.metric("Recommended new purchase",f"{rec['order_qty']} jin")
        m3.metric("Cost-based service fractile",f"{100*rec['critical_fractile']:.1f}%")
        st.write(f"**Method:** {result.model}, trained on {result.samples} past daily records.")
        st.write(f"**Order explanation:** Underage cost = NT${rec['shortage_cost_per_unit']:.2f}/jin; overage cost = NT${rec['leftover_cost_per_unit']:.2f}/jin. "
                 f"Target stock ≈ {rec['target_inventory']:.1f} jin, minus {available_inventory:.1f} jin of usable inventory.")
        st.caption(result.note)
        if source == "Synthetic sample":
            st.warning("Simulation only: model fitted to generated transactions. These recommendations are NOT validated for actual vendors.")
        else:
            st.warning("Real sales may underestimate demand on days when you ran out of stock. Verify stockout information before field use.")
        st.download_button("Download recommendation (CSV)",data=pd.DataFrame([{
            "date":str(next_day),"product":product,"data_source":source,"forecast_sales":result.estimate,
            "forecast_sigma_uncalibrated":result.sigma,"saleable_inventory":available_inventory,
            "recommended_order":rec["order_qty"],"cost_service_fractile":rec["critical_fractile"]
        }]).to_csv(index=False).encode("utf-8"),file_name="stallsense_recommendation.csv",mime="text/csv")
    st.divider()
    st.markdown("**Historical sales overview**")
    if not history.empty:
        st.line_chart(history.tail(45).set_index("date")["quantity_sold"])
        st.caption("Observed sales are censored by stockouts; true unmet demand is not directly observable.")

with backtest_tab:
    st.subheader("H3: Can AI lower leftover cost without increasing stockouts?")
    st.write("Walk-forward replay: at each date, the model trains only on preceding records. Both ordering strategies face the **same synthetic latent demand**.")
    if source != "Synthetic sample":
        st.warning("H3 replay is disabled for real transaction logs: the unobserved demand after stockout is unknown. A legitimate field test requires an unmet-demand estimate or an experiment.")
    else:
        eval_days = st.slider("Historical test window (days)",15,60,30,5)
        with st.spinner("Running chronological backtest..."):
            detail, metrics = backtest(history, days=eval_days)
        display = metrics[["strategy","leftover_cost","stockout_rate_pct","estimated_profit","average_order"]].copy()
        display.columns = ["Strategy","Leftover cost (NT$)","Stockout days (%)","Estimated profit (NT$)","Mean order (jin)"]
        st.dataframe(display.style.format({"Leftover cost (NT$)":"{:.0f}","Stockout days (%)":"{:.1f}","Estimated profit (NT$)":"{:.0f}","Mean order (jin)":"{:.1f}"}),use_container_width=True,hide_index=True)
        h3 = evaluate_h3(metrics)
        a,b,c = st.columns(3)
        a.metric("AI reduced leftover cost?", "YES" if h3["leftover_cost_reduced"] else "NO")
        b.metric("AI avoided higher stockout rate?", "YES" if h3["stockout_not_increased"] else "NO")
        c.metric("H3 met in simulation?", "YES" if h3["h3_met"] else "NO")
        st.caption("Important: this outcome applies only to synthetic data and the modeled assumptions. It is not evidence of measured commercial savings.")
        st.bar_chart(display.set_index("Strategy")[["Leftover cost (NT$)"]])
        st.download_button("Download reproducible replay rows (CSV)", data=detail.to_csv(index=False).encode("utf-8"),file_name="stallsense_h3_backtest.csv",mime="text/csv")
        with st.expander("Methodology and limitations"):
            st.markdown("""
- Strategy A: order yesterday's *observed* sales quantity.
- Strategy B: order the previous seven days' mean observed sales.
- Strategy C: forecast next-day sales using only previous sales, earlier forecast weather, holiday, and price; apply a newsvendor quantile.
- True demand is present **only in the synthetic dataset**. Real stockout days censor demand.
- Purchases are modeled as single-day perishable units with no carryover. Real selling, supplier packs, and preservation constraints are excluded.
- Performance varies by period and data-generating assumptions. H3 might fail and is reported without hiding the result.
""")

with roadmap_tab:
    st.subheader("System architecture and Stage II roadmap")
    st.code("""Vendor input (buttons / local SQLite)
          + weather forecast + holiday calendar
                         |
                Host CPU (Python)
          -> baseline + Ridge forecast
          -> deterministic newsvendor rule
          -> historical H3 replay / display
                         |
     Stage II, NOT implemented in this repository:
         ASUS UGen300 / Hailo-10H
         -> privacy-preserving footfall count
         -> local speech-to-text + explanations
         -> FPS, latency, wattage, 72h stability tests""", language="text")
    st.markdown("""
**Why local?** Reduce data sharing of cost and profit records, support intermittent connectivity, and plan on-device anonymous people-counting without face recognition.

**Hardware status:** No UGen300 has been used or benchmarked for this Stage I repository. Model compilation, driver compatibility, language tasks, latency, power and 72-hour operation remain **unverified**.

**User research status:** Vendor pain points and willingness to pay are hypotheses requiring interviews, not demonstrated facts.

**Target product:** Small traditional-market food vendors, with fixed-formula pricing and ordering decisions and manual confirmation.
""")
    st.markdown("See `README.md` and `docs/STAGE_II_ROADMAP.md` for reproducibility and limitations.")
