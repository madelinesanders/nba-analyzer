import streamlit as st
import duckdb
import os

# Config
PARQUET_URL = "s3://nba-analyzer-data-madeline/nba-data/latest/stats_df.parquet"

def load_duckdb_connection():
    con = duckdb.connect()
    con.execute("INSTALL httpfs;")
    con.execute("LOAD httpfs;")
    con.execute("SET s3_region='us-east-2';")
    con.execute(f"SET s3_access_key_id='{os.environ.get('AWS_ACCESS_KEY_ID')}';")
    con.execute(f"SET s3_secret_access_key='{os.environ.get('AWS_SECRET_ACCESS_KEY')}';")
    return con

st.title("🏀 NBA Player Stats Dashboard")
st.caption("Powered by DuckDB SQL + Streamlit")

try:
    con = load_duckdb_connection()

    tab1, tab2 = st.tabs(["🏀 Player View", "🏟️ Team View"])
    with tab1:
        # Load unique player names for dropdown
        player_names = con.execute(f"""
            SELECT DISTINCT PLAYER_NAME
            FROM read_parquet('{PARQUET_URL}')
            ORDER BY PLAYER_NAME
        """).fetchall()
        player_names = [row[0] for row in player_names]

        selected_player = st.selectbox("Select a Player", player_names)

        # Query player stats
        player_df = con.execute(f"""
            SELECT SEASON_ID, TEAM_ID, PTS, AST, REB, GP, PLAYER_NAME
            FROM read_parquet('{PARQUET_URL}')
            WHERE PLAYER_NAME = '{selected_player}'
            ORDER BY SEASON_ID
        """).df()

        st.subheader(f"{selected_player}'s Season Stats")
        st.dataframe(player_df)

        st.line_chart(player_df.set_index("SEASON_ID")[["PTS", "AST", "REB"]])

    with tab2:
        team_names = con.execute(f"""
            SELECT DISTINCT TEAM_ABBREVIATION
            FROM read_parquet('{PARQUET_URL}')
        """).fetchall()

        selected_team = ("Select a Team", team_names)

        st.subheader("Leading Scorer per Season")
        top_scorers_df = con.execute(f"""
            SELECT SEASON_ID, PLAYER_NAME, MAX(PTS) as Max_PTS
            FROM read_parquet('{PARQUET_URL}')
            WHERE TEAM_ABBREVIATION = '{selected_team}'
            GROUP BY SEASON_ID, PLAYER_NAME
            ORDER BY SEASON_ID
        """).df()

        st.dataframe(top_scorers_df)

        st.subheader("Team Totals per Season")
        team_totals_df = con.execute(f"""
            SELECT SEASON_ID, SUM(PTS) as Total_PTS, SUM(AST) as Total_AST, SUM(REB) as Total_REB
            FROM read_parquet('{PARQUET_URL}')
            WHERE TEAM_ABBREVIATION = '{selected_team}'
            GROUP BY SEASON_ID
            ORDER BY SEASON_ID
        """).df()

        st.bar_chart(team_totals_df.set_index("SEASON_ID"))

            

except Exception as e:
    st.error(f"Failed to load data: {e}")
