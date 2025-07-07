# player_bio.py
import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

# --------------------------------------------------
# 1) PAGE CONFIG & GLOBAL STYLES
# --------------------------------------------------
st.set_page_config(page_title="Footbin clone β101", layout="wide")
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 1.5rem;
            padding-left: 3rem;
            padding-right: 3rem;
            max-width: 95%;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 2) LOAD DATA
# --------------------------------------------------
DB_PATH = r"D:\Data Project\exercise\Football\database\clean_football.db"

@st.cache_data(show_spinner=False)
def load_players():
    with sqlite3.connect(DB_PATH) as conn:
        sql = """
            SELECT  player_id,
                    name,
                    first_name,
                    last_name,
                    country_of_birth,
                    country_of_citizenship,
                    date_of_birth,
                    position,
                    sub_position,
                    foot,
                    height_in_cm,
                    current_club_name,
                    market_value_in_eur
            FROM players
        """
        df = pd.read_sql(sql, conn)
    return df.drop_duplicates("player_id")

df_players = load_players()

# --------------------------------------------------
# 3) SEARCH BOX + AUTOCOMPLETE (show max 10)
# --------------------------------------------------
st.title("DeepPlayr Bio")

search = st.text_input("Enter player name", placeholder="e.g.Lewandowski")

suggested_name = None
if search:
    filtered = df_players[df_players["name"].str.contains(search, case=False, na=False)]
    suggested_name = st.selectbox(
        "Did you mean :",
        filtered["name"].head(5).tolist(),
        index=0 if not filtered.empty else None,
    )

# --------------------------------------------------
# 4) SHOW PLAYER BIO
# --------------------------------------------------
if suggested_name:
    p = df_players.query("name == @suggested_name").iloc[0]

    st.markdown("___")  # เส้นคั่นยาวเต็มหน้ากว้าง

    # ----- 4.1 LAYOUT image ⇆ data -----
    spacer_l, left, right, spacer_r = st.columns([1, 2, 5, 1])

    with left:
        # mock
        st.markdown(
            f"""
            <div style='width:180px;height:240px;background:#cfcfcf;
                        display:flex;align-items:center;justify-content:center;
                        font-weight:bold;color:#333;border-radius:6px;
                        border:1px solid #999;margin-bottom:0.75rem;'>
                {p['name']}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        dob = (
            datetime.strptime(p["date_of_birth"], "%Y-%m-%d").strftime("%d-%b-%Y")
            if p["date_of_birth"]
            else "-"
        )

        dob_str = p["date_of_birth"]
        if dob_str:
            birth_year = datetime.strptime(dob_str, "%Y-%m-%d").year
            age = datetime.now().year - birth_year
        else:
            age = "-"

        st.markdown(
            f"""
            **Name :** {p['name']}  
            **Age :** {age}  
            **Position :** {p['position']} | **Sub position :** {p['sub_position']}  
            **Country :** {p['country_of_birth']}  
            **Club :** {p['current_club_name']}  
            **Foot :** {p['foot'] or '-'}  
            **Height :** {int(p['height_in_cm']) if pd.notna(p['height_in_cm']) else '-'} cm  
            **Date of birth :** {dob}  
            **Market value :** €{int(p['market_value_in_eur']):,}  
            """
        )

    # ----- 4.2 ACTION BUTTONS -----
    g1, col_stat, col_tx, g2 = st.columns([4, 2, 2, 4])

    with col_stat:
        if st.button("Stat", use_container_width=True):
            st.session_state["player_name"] = p["name"]
            st.switch_page("pages/player_stat.py")

    with col_tx:
        if st.button("Transfer History", use_container_width=True):
            st.info("TODO → Transfer History page")
