import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.title('Player Stat')

# Load player_name from session state
player_name = st.session_state.get("player_name", None)

if not player_name:
    st.warning("Select Player Bio first")
    st.stop()

# --- Load appearance data from DB ---
DB_PATH = "D:/Data Project/exercise/Football/database/clean_football.db"

@st.cache_data
def load_appearance_data(name):
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql("SELECT * FROM appearances WHERE player_name = ?", conn, params=(name,))
    return df

@st.cache_data
def load_position_distribution(name):
    with sqlite3.connect(DB_PATH) as conn:
        sql = """
        SELECT gl.position
        FROM appearances ap
        JOIN game_lineups gl
            ON ap.game_id = gl.game_id AND ap.player_id = gl.player_id
        WHERE ap.player_name = ?
        """
        df = pd.read_sql(sql, conn, params=(name,))
    return df

df = load_appearance_data(player_name)
df_position = load_position_distribution(player_name)

# Convert 'date' to 'season' (e.g. 2013/14)
df["date"] = pd.to_datetime(df["date"], errors="coerce")
def convert_to_season(date):
    year = date.year
    if date.month >= 7:
        return f"{year}/{str(year+1)[-2:]}"
    else:
        return f"{year-1}/{str(year)[-2:]}"
df["season"] = df["date"].apply(convert_to_season)

# --- Aggregate basic stats ---
total_matches = len(df)
total_goals = df['goals'].sum()
total_assists = df['assists'].sum()
yellow_cards = df['yellow_cards'].sum()
red_cards = df['red_cards'].sum()
total_minutes = df["minutes_played"].sum()
mpg_display = f"{total_minutes / total_goals:.1f} min/goal" if total_goals > 0 else "No Goal"

# --- Display stats ---
if df.empty:
    st.info("No data available for this player.")
else:
    st.subheader(f"Stat of {player_name}")
    st.markdown(
        f"""
        **Matches Played:** {total_matches}  
        **Goals:** {total_goals}  
        **Assists:** {total_assists}  
        **Yellow Cards:** {yellow_cards}  
        **Red Cards:** {red_cards}  
        **Minutes per Goal:** {mpg_display}  
        """
    )

    # --- Plot Goals and Assists per Season ---
    season_summary = (
        df.groupby("season", as_index=False)[["goals", "assists"]]
        .sum()
        .sort_values("season")
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=season_summary["season"], y=season_summary["goals"],
                             mode="lines+markers", name="Goals"))
    fig.add_trace(go.Scatter(x=season_summary["season"], y=season_summary["assists"],
                             mode="lines+markers", name="Assists"))

    fig.update_layout(
        title="Goals & Assists per Season",
        xaxis_title="Season",
        yaxis_title="Count",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Pie Chart Position
    if not df_position.empty:
        pos_counts = df_position["position"].value_counts()
        pie_fig = go.Figure(
            data=[
                go.Pie(
                    labels=pos_counts.index,
                    values=pos_counts.values,
                    hole=0.4,
                    textinfo="label+percent",
                    pull=[0.03] * len(pos_counts)
                )
            ]
        )
        pie_fig.update_layout(
            title="Most Frequent Positions Played",
            template="plotly_dark"
        )

        st.subheader("Position Distribution")
        st.plotly_chart(pie_fig, use_container_width=True)
    else:
        st.info("No position data available for this player.")



    # --- Show raw appearance data ---
    st.dataframe(df)
