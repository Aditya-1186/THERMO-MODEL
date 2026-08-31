"""
Interactive Cp vs T Materials Database
Run locally:   streamlit run app.py
Deploy free:   push this folder to a GitHub repo, then deploy on
               https://share.streamlit.io (Streamlit Community Cloud)
               -> that gives you the "working link" required for submission.
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Cp-T Materials Explorer", layout="wide")

# ----------------------------- Data ---------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/materials_database.csv")
    return df

df = load_data()

def cp_of_T(row, T):
    A, B, C, D = row["A"], row["B"], row["C"], row["D"]
    T = np.asarray(T, dtype=float)
    return A + B*T + C*T**2 + D/np.where(T == 0, np.nan, T**2)

# ----------------------------- Sidebar --------------------------------
st.sidebar.title("🔍 Material Selection")

categories = sorted(df["category"].unique())
selected_categories = st.sidebar.multiselect("Category filter", categories, default=categories)

filtered = df[df["category"].isin(selected_categories)]

search = st.sidebar.text_input("Search by name or formula")
if search:
    mask = filtered["name"].str.contains(search, case=False, na=False) | \
           filtered["formula"].str.contains(search, case=False, na=False)
    filtered = filtered[mask]

selected_materials = st.sidebar.multiselect(
    "Select material(s) to plot",
    filtered["name"].tolist(),
    default=filtered["name"].tolist()[:1] if len(filtered) else [],
)

st.sidebar.markdown("---")
st.sidebar.subheader("Temperature range")
global_tmin = int(df["t_min"].min())
global_tmax = int(df["t_max"].max())
user_tmin, user_tmax = st.sidebar.slider(
    "User-defined T range (K)", global_tmin, global_tmax, (300, 1000)
)

st.sidebar.markdown("---")
quality_filter = st.sidebar.radio(
    "Data quality", ["All", "Verified (cited) only", "Placeholder only"], index=0
)

# ----------------------------- Main ------------------------------------
st.title("📊 Interactive Cp vs. Temperature Materials Database")
st.caption(f"{len(df)} materials across {len(categories)} classes — "
           f"{ (df['data_quality']=='verified').sum() } verified / "
           f"{ (df['data_quality']=='placeholder').sum() } placeholder (see sidebar)")

if quality_filter == "Verified (cited) only":
    plot_pool = filtered[filtered["data_quality"] == "verified"]
elif quality_filter == "Placeholder only":
    plot_pool = filtered[filtered["data_quality"] == "placeholder"]
else:
    plot_pool = filtered

selected_materials = [m for m in selected_materials if m in plot_pool["name"].values]

fig = go.Figure()
warnings = []

for mat_name in selected_materials:
    row = df[df["name"] == mat_name].iloc[0]
    t_lo, t_hi = row["t_min"], row["t_max"]
    plot_lo, plot_hi = max(user_tmin, 1), user_tmax

    T_full = np.linspace(plot_lo, plot_hi, 400)
    cp_full = cp_of_T(row, T_full)

    in_range = (T_full >= t_lo) & (T_full <= t_hi)
    out_range = ~in_range

    fig.add_trace(go.Scatter(
        x=T_full[in_range], y=cp_full[in_range], mode="lines",
        name=f"{mat_name} ({row['formula']})",
        hovertemplate="T=%{x:.1f} K<br>Cp=%{y:.3f}<extra>" + mat_name + "</extra>",
    ))
    if out_range.any():
        fig.add_trace(go.Scatter(
            x=T_full[out_range], y=cp_full[out_range], mode="lines",
            line=dict(dash="dot"), showlegend=False, opacity=0.4,
            hovertemplate="⚠ Outside valid range<br>T=%{x:.1f} K<extra></extra>",
        ))
        warnings.append(f"⚠️ **{mat_name}**: requested range [{user_tmin}, {user_tmax}] K "
                         f"extends beyond its valid equation range [{t_lo:.0f}, {t_hi:.0f}] K "
                         f"— dotted segment is extrapolated and not reliable.")

fig.update_layout(
    xaxis_title="Temperature, T (K)",
    yaxis_title="Specific Heat Capacity, Cp",
    hovermode="x unified",
    legend_title="Material",
    height=560,
    template="plotly_white",
)

st.plotly_chart(fig, use_container_width=True)

for w in warnings:
    st.warning(w)

if not selected_materials:
    st.info("Select one or more materials from the sidebar to plot Cp vs T.")

# ----------------------------- Details table ---------------------------
st.subheader("Material details")
if selected_materials:
    detail_cols = ["name", "formula", "category", "basis", "cp_unit", "t_min", "t_max",
                    "source", "data_quality"]
    st.dataframe(
        df[df["name"].isin(selected_materials)][detail_cols].set_index("name"),
        use_container_width=True,
    )

# ----------------------------- Comparison table -------------------------
if len(selected_materials) >= 2:
    st.subheader("Cp comparison at a chosen temperature")
    T_compare = st.slider("Compare Cp at T (K)", global_tmin, global_tmax, 500)
    comp_rows = []
    for mat_name in selected_materials:
        row = df[df["name"] == mat_name].iloc[0]
        val = float(cp_of_T(row, T_compare))
        in_range = row["t_min"] <= T_compare <= row["t_max"]
        comp_rows.append({"Material": mat_name, "Cp": round(val, 4),
                           "Unit": row["cp_unit"], "In valid range?": "✅" if in_range else "⚠️ No"})
    st.table(pd.DataFrame(comp_rows).set_index("Material"))

st.markdown("---")
st.caption("Model: Cp(T) = A + B·T + C·T² + D/T² (generalized Kelley/Shomate form). "
           "\"Verified\" rows use standard handbook coefficients (Kubaschewski & Alcock; "
           "Barin; NIST-JANAF). \"Placeholder\" rows use class-typical estimates pending "
           "replacement with cited literature/database values — see data/materials_database.csv "
           "column `data_quality`.")
