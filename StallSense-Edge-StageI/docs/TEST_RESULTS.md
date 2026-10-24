# Test evidence (October 13, 2026)

- `python -m pytest -q`: **5 tests passed**.
- `python -m compileall -q .`: passed (syntax compilation).
- H3 simulation: computed successfully for all three included synthetic products.
- The synthetic runs **do not satisfy** H3 under the default parameters: leftover costs fell but stockout-day rates increased compared with yesterday's-sales ordering. The app reports this instead of asserting a successful hypothesis.

**Testing limitation:** The build environment did not have Streamlit installed and could not reach the Python package index. Thus the browser interface itself could **not** be launch-tested here. Please run `python -m pip install -r requirements.txt` and `python -m streamlit run app.py` on a normal internet-connected computer, then confirm navigation and screenshots before using the GitHub URL in your submission.

**No UGen300 hardware was available**, so no edge deployment or speed measurements were performed.
