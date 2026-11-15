"""Interactive London boroughs dashboard.

    pip install -r requirements.txt
    streamlit run app.py
"""
import pathlib
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = pathlib.Path(__file__).resolve().parent
df = pd.read_csv(ROOT / "data" / "london_boroughs.csv")

st.set_page_config(page_title="London Boroughs", layout="wide")
st.title("🏙️ London Boroughs — Population & Density")
st.caption("Data: Wikipedia 'List of London boroughs' (2022 population estimates).")

# Filters
desig = st.sidebar.multiselect("Designation", sorted(df.designation.unique()), default=list(df.designation.unique()))
metric = st.sidebar.selectbox("Metric", ["population", "density_per_km2", "area_km2"])
view = df[df.designation.isin(desig)]

c1, c2, c3 = st.columns(3)
c1.metric("Boroughs", len(view))
c2.metric("Total population", f"{int(view.population.sum()):,}")
c3.metric("Avg density", f"{view.density_per_km2.mean():,.0f}/km²")

left, right = st.columns([3, 2])
with left:
    st.subheader(f"Boroughs by {metric.replace('_', ' ')}")
    fig = px.bar(view.sort_values(metric, ascending=True), x=metric, y="borough",
                 color="designation", orientation="h", height=650)
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader("Map")
    fig_map = px.scatter_mapbox(view, lat="lat", lon="lon", size="population",
                                color="density_per_km2", hover_name="borough",
                                color_continuous_scale="viridis", zoom=8.5, height=650,
                                mapbox_style="open-street-map")
    st.plotly_chart(fig_map, use_container_width=True)

st.subheader("Population vs Area")
fig_scatter = px.scatter(
    view,
    x="area_km2",
    y="population",
    size="density_per_km2",
    color="designation",
    hover_name="borough",
    hover_data={
        "area_km2": ":.1f",
        "population": ":,",
        "density_per_km2": ":,.0f",
        "designation": True,
    },
    size_max=28,
    labels={
        "area_km2": "Area (km²)",
        "population": "Population",
        "density_per_km2": "Density (/km²)",
        "designation": "Region",
    },
)
fig_scatter.update_layout(
    legend_title_text="Region",
    xaxis=dict(showgrid=True, gridcolor="rgba(200,200,200,0.2)"),
    yaxis=dict(showgrid=True, gridcolor="rgba(200,200,200,0.2)"),
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader("Borough Liveability Ranking")
# Proxy score: Higher area and lower density are weighted as 'more liveable'
# Normalized against the full dataset for consistent ranking
max_area = df["area_km2"].max()
max_dens = df["density_per_km2"].max()
min_dens = df["density_per_km2"].min()

orm_area = view["area_km2"] / max_area
orm_density = (max_dens - view["density_per_km2"]) / (max_dens - min_dens)
view_ranked = view.assign(liveability_score=((norm_area + norm_density) / 2 * 100).round(1))

st.dataframe(
    view_ranked.sort_values("liveability_score", ascending=False)[["borough", "liveability_score", "designation"]],
    use_container_width=True
)

st.subheader("Data")
st.dataframe(view, use_container_width=True)
