import pandas as pd
import time
import boto3
import duckdb
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players

def main():
    # Get all active players
    all_players = pd.DataFrame(players.get_players())
    player_ids = [row["id"] for _, row in all_players.iterrows() if row["is_active"]]

    dfs = []
    for player_id in player_ids[:10]:  # Only 10 for testing
        try:
            career = playercareerstats.PlayerCareerStats(player_id=player_id)
            career_df = career.get_data_frames()[0]
            dfs.append(career_df)
            time.sleep(0.1)
        except Exception as e:
            print(f"Error with player {player_id}: {e}")

    if not dfs:
        print("No data collected.")
        return

    stats_df = pd.concat(dfs, ignore_index=True)

    # Save to DuckDB
    db_path = "stats_df.duckdb"
    con = duckdb.connect(db_path)
    con.execute("CREATE TABLE stats AS SELECT * FROM stats_df")
    con.close()

    # Upload to S3
    s3 = boto3.client("s3")
    s3.upload_file(db_path, "nba-analyzer-data-madeline", "nba-data/stats_df.duckdb")
    print("Upload complete.")

if __name__ == "__main__":
    main()
