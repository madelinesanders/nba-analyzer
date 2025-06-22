import pandas as pd
import time
import boto3
import duckdb

from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
from nba_api.stats.library.http import NBAStatsHTTP  # <- added for header spoofing

# Spoof headers to mimic a browser and avoid being blocked
NBAStatsHTTP._HEADERS = {
    "Host": "stats.nba.com",
    "Connection": "keep-alive",
    "Accept": "application/json, text/plain, */*",
    "x-nba-stats-token": "true",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "x-nba-stats-origin": "stats",
    "Origin": "https://www.nba.com",
    "Referer": "https://www.nba.com/",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
}

def main():
    # Get all active NBA players
    all_players = pd.DataFrame(players.get_players())
    player_ids = [row["id"] for _, row in all_players.iterrows() if row["is_active"]]

    # For testing, just pull a few players
    dfs = []
    for player_id in player_ids[:2]:  # scale this up once it works
        print(f"Trying player {player_id}...", flush=True)
        try:
            career = playercareerstats.PlayerCareerStats(player_id=player_id)
            print(f"Retrieved data for player {player_id}", flush=True)
            career_df = career.get_data_frames()[0]
            dfs.append(career_df)
            print(f"Appended stats for player {player_id}", flush=True)
            time.sleep(0.1)
        except Exception as e:
            print(f"Error with player {player_id}: {e}", flush=True)

    if not dfs:
        print("No data collected.", flush=True)
        return

    # Combine data
    stats_df = pd.concat(dfs, ignore_index=True)

    # Save to DuckDB
    db_path = "stats_df.duckdb"
    con = duckdb.connect(db_path)
    con.execute("CREATE TABLE stats AS SELECT * FROM stats_df")
    con.close()

    # Upload to S3
    s3 = boto3.client("s3")
    bucket_name = "nba-analyzer-data-madeline"
    s3_key = "nba-data/stats_df.duckdb"
    try:
        s3.upload_file(db_path, bucket_name, s3_key)
        print(f"Upload complete: s3://{bucket_name}/{s3_key}", flush=True)
    except Exception as e:
        print(f"Upload failed: {e}", flush=True)

if __name__ == "__main__":
    main()
