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
    hover_data=["density_per_km2"],
    labels={
        "area_km2": "Area (km²)",
        "population": "Population",
        "density_per_km2": "Density (/km²)",
        "designation": "Region",
    },
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader("Data")
st.dataframe(view, use_container_width=True)
