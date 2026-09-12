"""Fetch the 'List of London boroughs' table from Wikipedia and produce a clean CSV.

    python src/prepare_data.py   ->  data/london_boroughs.csv
"""
import io, re, pathlib
import pandas as pd, requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
URL = "https://en.wikipedia.org/wiki/List_of_London_boroughs"

def main():
    html = requests.get(URL, headers={"User-Agent": "london-dataviz"}).text
    raw = next(t for t in pd.read_html(io.StringIO(html))
               if any("Borough" in str(c) for c in t.columns) and t.shape[0] >= 30)
    raw.columns = ["_".join(str(x) for x in c) if isinstance(c, tuple) else str(c) for c in raw.columns]

    def col(sub):
        return next(c for c in raw.columns if sub.lower() in c.lower())

    df = pd.DataFrame({
        "borough": raw[col("Borough")].str.replace(r"\[.*?\]", "", regex=True).str.strip(),
        "designation": raw[col("Designation")].str.strip(),
        "political_control": raw[col("Political control")].str.replace(r"\[.*?\]", "", regex=True).str.strip(),
        "area_km2": pd.to_numeric(raw[col("km2")], errors="coerce"),
        "population": pd.to_numeric(raw[col("Population")].astype(str).str.replace(r"[^0-9]", "", regex=True), errors="coerce"),
    })
    # decimal lat/lon out of the Location column ("...51.5607°N 0.1557°E")
    loc = raw[col("Location")].astype(str)
    df["lat"] = loc.str.extract(r"([\d.]+)°N").astype(float)
    lon = loc.str.extract(r"([\d.]+)°([EW])")
    df["lon"] = lon[0].astype(float) * lon[1].map({"E": 1, "W": -1})
    df["density_per_km2"] = (df["population"] / df["area_km2"]).round(0)

    df = df.dropna(subset=["population", "area_km2"]).sort_values("borough").reset_index(drop=True)
    out = ROOT / "data" / "london_boroughs.csv"
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} boroughs -> {out}")

if __name__ == "__main__":
    main()
