import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import duckdb
from settings import get_db_path

# --------------------------------------------------
# 1) PAGE HEADER
# --------------------------------------------------
st.title("📊 Player Stat")

# --------------------------------------------------
# 2) GET PLAYER NAME FROM SESSION
# --------------------------------------------------
player_name = st.session_state.get("player_name")
if not player_name:
    st.warning("Please select a player from the Bio page first.")
    st.stop()

# --------------------------------------------------
# 3) DB + LOADERS
# --------------------------------------------------
DB_PATH = get_db_path()

@st.cache_data
def load_appearances(name):
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql("SELECT * FROM appearances WHERE player_name = ?", conn, params=(name,))
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df

@st.cache_data
def load_positions(name):
    with sqlite3.connect(DB_PATH) as conn:
        q = """
        SELECT gl.position, gl.date, gl.club_id
        FROM appearances ap
        JOIN game_lineups gl
          ON ap.game_id = gl.game_id AND ap.player_id = gl.player_id
        WHERE ap.player_name = ?
        """
        df = pd.read_sql(q, conn, params=(name,))
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df

@st.cache_data
def load_club_map():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql("SELECT club_id, name FROM clubs", conn)
    return dict(zip(df["club_id"], df["name"]))

# --------------------------------------------------
# 4) LOAD DATA
# --------------------------------------------------
df_appear = load_appearances(player_name)
df_pos    = load_positions(player_name)
id2name   = load_club_map()

if df_appear.empty:
    st.info("No data for this player.")
    st.stop()

# --------------------------------------------------
# 5) FILTERS
# --------------------------------------------------
unique_ids = df_appear["player_club_id"].fillna(-1).astype(int).unique()
unique_names = [id2name.get(cid, f"Club {cid}") for cid in unique_ids]

sel_names = st.multiselect("🧑‍🤝‍🧑 Select team(s)", unique_names, default=unique_names)
sel_ids   = [k for k, v in id2name.items() if v in sel_names]

min_dt, max_dt = df_appear["date"].min().date(), df_appear["date"].max().date()
start_dt, end_dt = st.date_input("📆 Select date range", (min_dt, max_dt),
                                 min_value=min_dt, max_value=max_dt)

mask_app = df_appear["player_club_id"].astype(int).isin(sel_ids) & df_appear["date"].dt.date.between(start_dt, end_dt)
df_filt = df_appear.loc[mask_app].copy()

mask_pos = df_pos["club_id"].astype(int).isin(sel_ids) & df_pos["date"].dt.date.between(start_dt, end_dt)
df_pos_filt = df_pos.loc[mask_pos]

if df_filt.empty:
    st.info("No appearances in selected filters.")
    st.stop()

# --------------------------------------------------
# 6) SEASON COLUMN
# --------------------------------------------------
def to_season(ts):
    y = ts.year
    return f"{y}/{str(y+1)[-2:]}" if ts.month >= 7 else f"{y-1}/{str(y)[-2:]}"
df_filt["season"] = df_filt["date"].apply(to_season)
df_pos_filt["season"] = df_pos_filt["date"].apply(to_season)

# --------------------------------------------------
# 7) OVERALL STAT
# --------------------------------------------------
st.subheader(f"Stat overview · {player_name}")
st.markdown(
    f"""
**Matches Played:** {len(df_filt)}  
**Goals:** {df_filt['goals'].sum()}  
**Assists:** {df_filt['assists'].sum()}  
**Yellow Cards:** {df_filt['yellow_cards'].sum()}  
**Red Cards:** {df_filt['red_cards'].sum()}  
**Minutes per Goal:** {f"{df_filt['minutes_played'].sum() / df_filt['goals'].sum():.1f} min/goal" if df_filt['goals'].sum() else "—"}  
"""
)

# --------------------------------------------------
# 9) GOALS & ASSISTS PER SEASON  – TWO MODES
# --------------------------------------------------

st.subheader("Goals & Assists per Season")

chart_mode = st.radio(
    "Visualisation mode",
    ["Single line (with team label)", "Compare teams (multi‑line)"],
    horizontal=True,
    help="Switch between overall curve and team‑by‑team comparison"
)

# ---------- COMMON PREP: build season, team mapping ----------
season_team_summary = (
    df_filt
      .groupby(["season", "player_club_id"], as_index=False)
      .agg(goals=("goals", "sum"), assists=("assists", "sum"))
)

# Build readable team name column
season_team_summary["team_name"] = season_team_summary["player_club_id"].apply(
    lambda cid: id2name.get(cid, f"Club {cid}")
)

# ---------- MODE 1 : Single line with team label ----------
if chart_mode.startswith("Single"):

    # Aggregate per season (sum across teams)
    summary_single = (
        season_team_summary
          .groupby("season", as_index=False)[["goals", "assists"]]
          .sum()
    )

    # Create label: 2021/22 (Chelsea, Inter)
    team_per_season = (
        season_team_summary.groupby("season")["team_name"]
        .apply(lambda x: ", ".join(sorted(set(x))))
        .reset_index()
    )
    summary_single = summary_single.merge(team_per_season, on="season")
    summary_single["season_label"] = summary_single["season"] + " (" + summary_single["team_name"] + ")"

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=summary_single["season_label"], y=summary_single["goals"],
            mode="lines+markers", name="Goals"
        )
    )
    fig.add_trace(
        go.Scatter(
            x=summary_single["season_label"], y=summary_single["assists"],
            mode="lines+markers", name="Assists"
        )
    )
    fig.update_layout(
        title="Goals & Assists per Season",
        xaxis_title="Season (Team)",
        yaxis_title="Count",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------- MODE 2 : Multi‑line per team ----------
else:
    # Pivot so each team is its own column
    pivot_goals   = season_team_summary.pivot(index="season", columns="team_name", values="goals").fillna(0)
    pivot_assists = season_team_summary.pivot(index="season", columns="team_name", values="assists").fillna(0)

    # Plot Goals
    fig_goals = go.Figure()
    for team in pivot_goals.columns:
        fig_goals.add_trace(go.Scatter(
            x=pivot_goals.index, y=pivot_goals[team],
            mode="lines+markers", name=team
        ))
    fig_goals.update_layout(
        title="Goals per Season (by Team)",
        xaxis_title="Season",
        yaxis_title="Goals",
        template="plotly_dark"
    )
    st.plotly_chart(fig_goals, use_container_width=True)

    # Plot Assists
    fig_ast = go.Figure()
    for team in pivot_assists.columns:
        fig_ast.add_trace(go.Scatter(
            x=pivot_assists.index, y=pivot_assists[team],
            mode="lines+markers", name=team
        ))
    fig_ast.update_layout(
        title="Assists per Season (by Team)",
        xaxis_title="Season",
        yaxis_title="Assists",
        template="plotly_dark"
    )
    st.plotly_chart(fig_ast, use_container_width=True)

# --------------------------------------------------
# 9) POSITION DISTRIBUTION
# --------------------------------------------------
if not df_pos_filt.empty:
    pos_counts = df_pos_filt["position"].value_counts()
    fig_pie = go.Figure(data=[go.Pie(
        labels=pos_counts.index,
        values=pos_counts.values,
        hole=0.4,
        textinfo="label+percent",
        pull=[0.03]*len(pos_counts)
    )])
    fig_pie.update_layout(title="Most Frequent Positions Played", template="plotly_dark")
    st.subheader("Position Distribution")
    st.plotly_chart(fig_pie, use_container_width=True)

# --------------------------------------------------
# 10) RAW DATA EXPANDER
# --------------------------------------------------
with st.expander("📄 Raw appearance data"):
    st.dataframe(df_filt, use_container_width=True)

# --------------------------------------------------
# 11) SQL QUERY EXPLORER
# --------------------------------------------------
st.subheader("🔍 SQL Query Explorer")

con = duckdb.connect()
con.register("df_filt", df_filt)
con.register("df_pos_filt", df_pos_filt)

sql_input = st.text_area("Enter SQL query", "SELECT * FROM df_filt LIMIT 100")
try:
    df_query = con.execute(sql_input).df()
    st.dataframe(df_query, use_container_width=True)
except Exception as e:
    st.error(f"❌ SQL Error: {e}")
