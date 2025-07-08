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

except Exception as e:
    st.error(f"Failed to load data: {e}")
