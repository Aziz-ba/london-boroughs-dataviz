"""Analyze the London boroughs dataset and generate charts + insights.

    python src/analysis.py
"""
import pathlib
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parent.parent
df = pd.read_csv(ROOT / "data" / "london_boroughs.csv")
A = ROOT / "assets"; A.mkdir(exist_ok=True)
BLUE, RED = "#29B5E8", "#EE4C2C"

# 1) Top 10 by population
top = df.nlargest(10, "population")
ax = top.plot.barh(x="borough", y="population", color=BLUE, legend=False, figsize=(7, 5))
ax.invert_yaxis(); ax.set_xlabel("Population (2022)"); ax.set_title("Top 10 London boroughs by population")
plt.tight_layout(); plt.savefig(A / "top_population.png", dpi=130); plt.close()

# 2) Top 10 by density
topd = df.nlargest(10, "density_per_km2")
ax = topd.plot.barh(x="borough", y="density_per_km2", color=RED, legend=False, figsize=(7, 5))
ax.invert_yaxis(); ax.set_xlabel("People per km²"); ax.set_title("Top 10 densest London boroughs")
plt.tight_layout(); plt.savefig(A / "top_density.png", dpi=130); plt.close()

# 3) Area vs population, colored by inner/outer
fig, ax = plt.subplots(figsize=(7, 5))
for desig, g in df.groupby("designation"):
    ax.scatter(g["area_km2"], g["population"], label=desig, s=60, alpha=0.8)
ax.set_xlabel("Area (km²)"); ax.set_ylabel("Population"); ax.set_title("Area vs population — Inner vs Outer London")
ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig(A / "area_vs_population.png", dpi=130); plt.close()

# 4) Simple geographic scatter (lon/lat) sized by population
fig, ax = plt.subplots(figsize=(6.5, 6))
sc = ax.scatter(df["lon"], df["lat"], s=df["population"] / 800, c=df["density_per_km2"], cmap="viridis", alpha=0.8)
ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude"); ax.set_title("London boroughs (size=pop, color=density)")
plt.colorbar(sc, label="Density / km²"); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig(A / "map_scatter.png", dpi=130); plt.close()

# ---- insights ----
inner = df[df.designation == "Inner"]; outer = df[df.designation == "Outer"]
print("=== LONDON BOROUGHS — KEY INSIGHTS ===")
print(f"Boroughs: {len(df)} | total population: {int(df.population.sum()):,}")
print(f"Largest by population: {top.iloc[0].borough} ({int(top.iloc[0].population):,})")
print(f"Densest: {topd.iloc[0].borough} ({int(topd.iloc[0].density_per_km2):,}/km²)")
print(f"Least dense: {df.nsmallest(1,'density_per_km2').iloc[0].borough} ({int(df.density_per_km2.min()):,}/km²)")
print(f"Inner London avg density: {inner.density_per_km2.mean():,.0f}/km²  vs  Outer: {outer.density_per_km2.mean():,.0f}/km²")
print(f"Density range: {int(df.density_per_km2.max()/df.density_per_km2.min())}x between densest and sparsest")
print("Political control:")
print(df.political_control.value_counts().to_string())
print("Charts written to assets/.")
