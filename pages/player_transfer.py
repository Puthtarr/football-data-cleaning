# pages/player_transfer.py
import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from collections import defaultdict
from settings import get_db_path

# --------------------------
# PAGE HEADER
# --------------------------
st.title("🔁 Player Transfer History")

player_name = st.session_state.get("player_name")
if not player_name:
    st.warning("Please select a player from the Bio page first.")
    st.stop()

# --------------------------
# LOAD DATA
# --------------------------
DB_PATH = get_db_path()

@st.cache_data
def load_transfers(name):
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql("SELECT * FROM transfers WHERE player_name = ?", conn, params=(name,))
    df["transfer_date"] = pd.to_datetime(df["transfer_date"], errors="coerce")
    return df.sort_values("transfer_date")

@st.cache_data
def load_club_map():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql("SELECT club_id, name FROM clubs", conn)
    return dict(zip(df["club_id"], df["name"]))

df_transfers = load_transfers(player_name)
id2name = load_club_map()

if df_transfers.empty:
    st.info("No transfer data available.")
    st.stop()

# --------------------------
# SEASON HELPER
# --------------------------
def to_season(dt):
    y = dt.year
    return f"{y}/{str(y+1)[-2:]}" if dt.month >= 7 else f"{y-1}/{str(y)[-2:]}"

df_transfers["transfer_season"] = df_transfers["transfer_date"].apply(to_season)
df_transfers["to_club_name"] = df_transfers["to_club_id"].apply(lambda cid: id2name.get(cid, f"Club {cid}"))

# Cleaned data for plot
cleaned_df = df_transfers[["transfer_season", "to_club_name"]].dropna()

# --------------------------
# TRANSFER TIMELINE
# --------------------------
st.subheader("Transfer Seasons (Hover for club)")

seasons = cleaned_df["transfer_season"].tolist()[::-1]
clubs = cleaned_df["to_club_name"].tolist()[::-1]

# Fix overlapping: give same-season transfers different y-offsets
y_vals = []
season_counts = defaultdict(int)
for season in seasons:
    y_offset = 1 + 0.05 * season_counts[season]
    y_vals.append(y_offset)
    season_counts[season] += 1

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=seasons,
    y=y_vals,
    mode="lines+markers+text",
    line=dict(color="white", dash="dot"),
    text=clubs,
    textposition="top center",
    marker=dict(size=14),
    hovertemplate="Season: %{x}<br>Club: %{text}"
))

# Add directional arrows
for i in range(len(seasons) - 1):
    fig.add_annotation(
        x=seasons[i+1],
        y=y_vals[i+1],
        ax=seasons[i],
        ay=y_vals[i],
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True,
        arrowhead=3,
        arrowsize=1,
        arrowwidth=1,
        arrowcolor="lightblue"
    )

fig.update_layout(
    height=300,
    margin=dict(t=30, b=20),
    xaxis_title="Season",
    yaxis=dict(visible=False),
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)