import streamlit as st
import duckdb
import os
import plotly.express as px

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
            SELECT SEASON_ID, TEAM_NAME, PTS, AST, REB, GP
            FROM read_parquet('{PARQUET_URL}')
            WHERE PLAYER_NAME = '{selected_player}' AND TEAM_ID != 0
            ORDER BY SEASON_ID
        """).df()

        st.subheader(f"{selected_player}'s Season Stats")
        st.dataframe(player_df)

        if not player_df.empty:
            fig = px.line(
                player_df,
                x="SEASON_ID",
                y=["PTS", "AST", "REB"],
                markers=True,
                labels={"value": "Stat Value", "SEASON_ID": "Season", "variable": "Stat"},
                title=f"{selected_player}'s Season Stats (by Team)",
            )
            fig.update_layout(
                xaxis_title="Season",
                yaxis_title="Stat Value",
                legend_title="Stat",
                template="plotly_dark",
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No stats available for this player with a valid team.")

    
    with tab2:
        # Get the most recent season_id
        most_recent_season = con.execute(f"""
            SELECT MAX(SEASON_ID) FROM read_parquet('{PARQUET_URL}')
        """).fetchone()[0]

        # Load team abbreviations for the most recent season only
        team_names = con.execute(f"""
            SELECT DISTINCT TEAM_ABBREVIATION
            FROM read_parquet('{PARQUET_URL}')
            WHERE SEASON_ID = '{most_recent_season}'
            ORDER BY TEAM_ABBREVIATION
        """).fetchall()
        team_names = [row[0] for row in team_names]

        selected_team = st.selectbox("Select a Team", team_names)

        team_players_df = con.execute(f"""
            SELECT PLAYER_NAME, PTS, AST, REB, GP
            FROM read_parquet('{PARQUET_URL}')
            WHERE TEAM_ABBREVIATION = '{selected_team}' AND SEASON_ID = '{most_recent_season}'
            ORDER BY PTS DESC
        """).df()
        st.subheader(f"Players for {selected_team} - {most_recent_season}")
        st.dataframe(team_players_df)

        team_totals_df = con.execute(f"""
            SELECT 
                SUM(PTS) AS Total_PTS, 
                SUM(AST) AS Total_AST, 
                SUM(REB) AS Total_REB,
                SUM(GP) AS Total_GP
            FROM read_parquet('{PARQUET_URL}')
            WHERE TEAM_ABBREVIATION = '{selected_team}' AND SEASON_ID = '{most_recent_season}'
        """).df()
        st.subheader(f"Team Totals for {selected_team} - {most_recent_season}")
        st.dataframe(team_totals_df)

        st.subheader(f"⭐ Stat Leaders for {selected_team} - {most_recent_season}")
        stat_leaders_df = con.execute(f"""
            WITH team_season_data AS (
                SELECT *
                FROM read_parquet('{PARQUET_URL}')
                WHERE TEAM_ABBREVIATION = '{selected_team}' AND SEASON_ID = '{most_recent_season}'
            ),
            pts_leader AS (
                SELECT PLAYER_NAME, PTS FROM team_season_data
                ORDER BY PTS DESC LIMIT 1
            ),
            ast_leader AS (
                SELECT PLAYER_NAME, AST FROM team_season_data
                ORDER BY AST DESC LIMIT 1
            ),
            reb_leader AS (
                SELECT PLAYER_NAME, REB FROM team_season_data
                ORDER BY REB DESC LIMIT 1
            )
            SELECT 
                (SELECT PLAYER_NAME FROM pts_leader) AS Top_Scorer,
                (SELECT PTS FROM pts_leader) AS Points,
                (SELECT PLAYER_NAME FROM ast_leader) AS Top_Assist,
                (SELECT AST FROM ast_leader) AS Assists,
                (SELECT PLAYER_NAME FROM reb_leader) AS Top_Rebounder,
                (SELECT REB FROM reb_leader) AS Rebounds
        """).df()

        st.dataframe(stat_leaders_df)


            

except Exception as e:
    st.error(f"Failed to load data: {e}")
