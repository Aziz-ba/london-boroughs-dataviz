"""Fetch the 'List of London boroughs' table from Wikipedia and produce a clean CSV.

    python src/prepare_data.py   ->  data/london_boroughs.csv
"""
from datetime import datetime
import io, pathlib
import pandas as pd, requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
URL = "https://en.wikipedia.org/wiki/List_of_London_boroughs"

def fetch_raw_table(url: str = URL) -> pd.DataFrame:
    """Fetch the main London boroughs table from Wikipedia with error handling."""
    headers = {"User-Agent": "london-boroughs-dataviz/1.0"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()

    tables = pd.read_html(io.StringIO(resp.text))
    raw = next(t for t in tables if any("Borough" in str(c) for c in t.columns) and t.shape[0] >= 30)
    raw.columns = ["_".join(str(x) for x in c) if isinstance(c, tuple) else str(c) for c in raw.columns]
    return raw


def clean_borough_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Clean raw Wikipedia table into a structured borough DataFrame."""
    def col(sub):
        return next(c for c in raw.columns if sub.lower() in c.lower())

    df = pd.DataFrame({
        "borough": raw[col("Borough")].str.replace(r"\[.*?\]", "", regex=True).str.strip(),
        "designation": raw[col("Designation")].str.strip(),
        "political_control": raw[col("Political control")].str.replace(r"\[.*?\]", "", regex=True).str.strip(),
        "area_km2": pd.to_numeric(raw[col("km2")], errors="coerce"),
        "population": pd.to_numeric(raw[col("Population")].astype(str).str.replace(r"[^0-9]", "", regex=True), errors="coerce"),
    })
    loc = raw[col("Location")].astype(str)
    df["lat"] = loc.str.extract(r"([\d.]+)°N").astype(float)
    lon = loc.str.extract(r"([\d.]+)°([EW])")
    df["lon"] = lon[0].astype(float) * lon[1].map({"E": 1, "W": -1})
    df["density_per_km2"] = (df["population"] / df["area_km2"]).round(0)

    df = df.dropna(subset=["population", "area_km2"]).sort_values("borough").reset_index(drop=True)
    if df.empty:
        raise ValueError("Cleaned borough dataset is empty.")
    return df


def refresh_data(out_path: pathlib.Path = None) -> pd.DataFrame:
    """Re-scrape Wikipedia table and update the London boroughs CSV dataset."""
    if out_path is None:
        out_path = ROOT / "data" / "london_boroughs.csv"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    raw = fetch_raw_table()
    df = clean_borough_data(raw)
    df.to_csv(out_path, index=False)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Refreshed data for {len(df)} boroughs -> {out_path}")
    return df


def main():
    refresh_data()


if __name__ == "__main__":
    main()
