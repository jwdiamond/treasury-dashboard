"""
export_dashboard_data.py
------------------------
Reads the CSV files produced by treasury_market_credit_v3.py and writes
data/dashboard_data.js for the static public dashboard.

Usage:
    python export_dashboard_data.py

Expected layout:
    Treasurydebt/
        treasury_market_credit_v3.py
        dashboard/
            index.html
            styles.css
            dashboard.js
            export_dashboard_data.py
            data/
        treasury_output/
            credit_market_history.csv
            treasury_maturity_buckets.csv
            treasury_security_summary.csv
            treasury_maturity_wall.csv
            treasury_refinancing_summary.csv
            treasury_duration_by_class.csv
            ...

If your treasury_output directory is somewhere else, change OUTPUT_DIR below.
"""

from pathlib import Path
import json
import pandas as pd

HERE = Path(__file__).resolve().parent
OUTPUT_DIR = HERE.parent / "treasury_output"
DATA_OUT = HERE / "data" / "dashboard_data.js"

def read(name):
    p = OUTPUT_DIR / name
    if not p.exists():
        raise FileNotFoundError(f"Missing {p}")
    return pd.read_csv(p)

credit = read("credit_market_history.csv")
buckets = read("treasury_maturity_buckets.csv")
summary = read("treasury_security_summary.csv")
refi = read("treasury_refinancing_summary.csv")
dur = read("treasury_duration_by_class.csv")

# Maturity wall is optional for V1; retain if available.
wall_path = OUTPUT_DIR / "treasury_maturity_wall.csv"
wall = pd.read_csv(wall_path) if wall_path.exists() else pd.DataFrame()

# Security-level file lets us recover total marketable debt and latest MSPD date.
security_path = OUTPUT_DIR / "treasury_latest_mspd_clean.csv"
sec = pd.read_csv(security_path) if security_path.exists() else pd.DataFrame()

credit["date"] = pd.to_datetime(credit["date"], errors="coerce")
credit = credit.dropna(subset=["date"]).sort_values("date")
latest = credit.dropna(subset=["ust_10y_pct","bbb_oas_bp"]).iloc[-1]

if not sec.empty:
    total_debt = pd.to_numeric(sec["outstanding_amt"], errors="coerce").sum() / 1e6
    maturity_dates = pd.to_datetime(sec["maturity_date"], errors="coerce")
    # Snapshot date is not always stored as a column. Leave blank if unavailable.
else:
    total_debt = float(summary["outstanding_trillions"].sum())

# WAM from security summary, weighted by amount.
wam = (summary["outstanding_trillions"] * summary["weighted_avg_maturity_years"]).sum() / summary["outstanding_trillions"].sum()

# Aggregate nominal modified duration across Bills/Notes/Bonds, weighted by amounts.
nom = dur[dur["security_class"].isin(["Bills","Notes","Bonds"])].copy()
moddur = (nom["outstanding_trillions"] * nom["modified_duration"]).sum() / nom["outstanding_trillions"].sum()

history = []
for _, r in credit.iterrows():
    history.append({
        "date": r["date"].date().isoformat(),
        "ust10": None if pd.isna(r.get("ust_10y_pct")) else float(r["ust_10y_pct"]),
        "real10": None if pd.isna(r.get("ust_10y_real_pct")) else float(r["ust_10y_real_pct"]),
        "ig": None if pd.isna(r.get("ig_oas_bp")) else float(r["ig_oas_bp"]),
        "bbb": None if pd.isna(r.get("bbb_oas_bp")) else float(r["bbb_oas_bp"]),
        "hy": None if pd.isna(r.get("hy_oas_bp")) else float(r["hy_oas_bp"]),
        "ust10_5d_bp": None if pd.isna(r.get("ust_10y_chg_5d_bp")) else float(r["ust_10y_chg_5d_bp"]),
        "bbb_5d_bp": None if pd.isna(r.get("bbb_oas_chg_5d_bp")) else float(r["bbb_oas_chg_5d_bp"]),
    })

data = {
    "meta": {
        "market_date": latest["date"].date().isoformat(),
        "mspd_date": "",
        "curve_date": "",
        "generated": pd.Timestamp.now().date().isoformat(),
    },
    "market": {
        "ust10": float(latest["ust_10y_pct"]),
        "real10": float(latest["ust_10y_real_pct"]),
        "ig_oas": float(latest["ig_oas_bp"]),
        "bbb_oas": float(latest["bbb_oas_bp"]),
        "hy_oas": float(latest["hy_oas_bp"]),
        "ust10_1d_bp": float(latest["ust_10y_chg_1d_bp"]),
        "bbb_1d_bp": float(latest["bbb_oas_chg_1d_bp"]),
        "ust10_5d_bp": float(latest["ust_10y_chg_5d_bp"]),
        "bbb_5d_bp": float(latest["bbb_oas_chg_5d_bp"]),
        "regime": str(latest["regime_5d"]).capitalize(),
        "alert_1d": bool(latest["double_tightening_1d"]),
        "alert_5d": bool(latest["double_tightening_5d"]),
    },
    "debt": {
        "marketable_debt_trillions": float(total_debt),
        "wam_years": float(wam),
        "modified_duration_years": float(moddur),
        "maturity_buckets": [
            {"horizon": f"{int(r.horizon_years)} year" + ("s" if int(r.horizon_years) != 1 else ""),
             "amount": float(r.amount_trillions), "share": float(r.share_pct)}
            for _, r in buckets.iterrows()
        ],
        "composition": [
            {"security": str(r.security_class), "amount": float(r.outstanding_trillions),
             "share": float(r.share_pct), "wam": float(r.weighted_avg_maturity_years)}
            for _, r in summary.iterrows()
        ],
    },
    "refinancing": [
        {"year": int(r.maturity_year), "maturing": float(r.debt_maturing_trillions),
         "coupon": float(r.avg_existing_coupon_pct), "replacement": float(r.avg_replacement_yield_pct),
         "reset_bp": float(r.avg_rate_change_bp), "interest_change": float(r.annual_interest_change_billions)}
        for _, r in refi.iterrows()
    ],
    "credit_history": history,
    "maturity_wall": wall.to_dict(orient="records") if not wall.empty else [],
}

DATA_OUT.parent.mkdir(parents=True, exist_ok=True)
DATA_OUT.write_text("window.DASHBOARD_DATA = " + json.dumps(data, allow_nan=False) + ";\n", encoding="utf-8")
print(f"Wrote {DATA_OUT}")
print(f"Latest market date: {data['meta']['market_date']}")
