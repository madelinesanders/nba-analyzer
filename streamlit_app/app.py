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
        # Get all teams from latest available season per player
        team_names = con.execute(f"""
            WITH latest_season AS (
                SELECT PLAYER_NAME, MAX(SEASON_ID) AS max_season
                FROM read_parquet('{PARQUET_URL}')
                GROUP BY PLAYER_NAME
            ),
            latest_team_data AS (
                SELECT r.PLAYER_NAME, r.SEASON_ID, r.TEAM_ABBREVIATION
                FROM read_parquet('{PARQUET_URL}') r
                JOIN latest_season l
                ON r.PLAYER_NAME = l.PLAYER_NAME AND r.SEASON_ID = l.max_season
            )
            SELECT DISTINCT TEAM_ABBREVIATION
            FROM latest_team_data
            ORDER BY TEAM_ABBREVIATION
        """).fetchall()
        team_names = [row[0] for row in team_names]

        selected_team = st.selectbox("Select a Team", team_names)

        # Subset: Only use each player's most recent season
        st.subheader("Leading Scorer per Season")
        top_scorers_df = con.execute(f"""
            WITH latest_season AS (
                SELECT PLAYER_NAME, MAX(SEASON_ID) AS max_season
                FROM read_parquet('{PARQUET_URL}')
                GROUP BY PLAYER_NAME
            ),
            latest_team_data AS (
                SELECT r.*
                FROM read_parquet('{PARQUET_URL}') r
                JOIN latest_season l
                ON r.PLAYER_NAME = l.PLAYER_NAME AND r.SEASON_ID = l.max_season
            ),
            team_data AS (
                SELECT *
                FROM latest_team_data
                WHERE TEAM_ABBREVIATION = '{selected_team}'
            )
            SELECT SEASON_ID, PLAYER_NAME, PTS
            FROM team_data
            ORDER BY PTS DESC
        """).df()
        st.dataframe(top_scorers_df)

        st.subheader("Team Totals (Most Recent Season per Player)")
        team_totals_df = con.execute(f"""
            WITH latest_season AS (
                SELECT PLAYER_NAME, MAX(SEASON_ID) AS max_season
                FROM read_parquet('{PARQUET_URL}')
                GROUP BY PLAYER_NAME
            ),
            latest_team_data AS (
                SELECT r.*
                FROM read_parquet('{PARQUET_URL}') r
                JOIN latest_season l
                ON r.PLAYER_NAME = l.PLAYER_NAME AND r.SEASON_ID = l.max_season
            )
            SELECT SEASON_ID, SUM(PTS) AS Total_PTS, SUM(AST) AS Total_AST, SUM(REB) AS Total_REB
            FROM latest_team_data
            WHERE TEAM_ABBREVIATION = '{selected_team}'
            GROUP BY SEASON_ID
            ORDER BY SEASON_ID
        """).df()
        st.bar_chart(team_totals_df.set_index("SEASON_ID"))

            

except Exception as e:
    st.error(f"Failed to load data: {e}")
