import pandas as pd
import time
import boto3
import duckdb
import logging
from datetime import datetime
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/madelinesanders/Projects/nba-analyzer/etl/etl.log'),
        logging.StreamHandler()
    ]
)

def main():
    logging.info("Starting NBA Data ETL")

    try:
        # Get all active NBA players
        all_players = pd.DataFrame(players.get_players())
        player_ids = [row["id"] for _, row in all_players.iterrows() if row["is_active"]]

        dfs = []
        logging.info(f"Fetching data for {len(player_ids[:100])} players...")

        for player_id in player_ids[:100]:  # Adjust slice to scale up
            try:
                career = playercareerstats.PlayerCareerStats(player_id=player_id)
                career_df = career.get_data_frames()[0]
                player_name = all_players.loc[all_players["id"] == player_id, "full_name"].values[0]
                career_df["PLAYER_NAME"] = player_name
                dfs.append(career_df)
                logging.info(f"✓ Added player {player_id}, {len(career_df)} rows")
                time.sleep(0.75)  # throttle requests slightly
            except Exception as e:
                logging.warning(f"⚠️ Failed for player {player_id}: {e}")

        if not dfs:
            logging.warning("No data collected.")
            return

        stats_df = pd.concat(dfs, ignore_index=True)
        logging.info(f"Collected {len(stats_df)} total records.")

        # File paths and timestamp
        timestamp = datetime.now().strftime('%Y%m%d')
        duckdb_path = f"stats_df_{timestamp}.duckdb"
        parquet_path = f"stats_df_{timestamp}.parquet"
        csv_path = f"stats_df_{timestamp}.csv"

        # Save to DuckDB
        con = duckdb.connect(duckdb_path)
        con.execute("DROP TABLE IF EXISTS stats")
        con.execute("CREATE TABLE stats AS SELECT * FROM stats_df")
        con.close()
        logging.info("Saved data to DuckDB.")

        # Save as Parquet and CSV
        stats_df.to_parquet(parquet_path, index=False)
        stats_df.to_csv(csv_path, index=False)
        logging.info("Saved data as Parquet and CSV.")

        # Upload to S3
        s3 = boto3.client("s3")
        bucket = "nba-analyzer-data-madeline"

        # Upload timestamped versions
        s3.upload_file(duckdb_path, bucket, f"nba-data/stats_df_{timestamp}.duckdb")
        s3.upload_file(parquet_path, bucket, f"nba-data/stats_df_{timestamp}.parquet")
        s3.upload_file(csv_path, bucket, f"nba-data/stats_df_{timestamp}.csv")

        # Upload "latest" versions
        s3.upload_file(duckdb_path, bucket, "nba-data/latest/stats_df.duckdb")
        s3.upload_file(parquet_path, bucket, "nba-data/latest/stats_df.parquet")
        s3.upload_file(csv_path, bucket, "nba-data/latest/stats_df.csv")

        logging.info("Upload to S3 complete.")
        logging.info("ETL Finished Successfully")

    except Exception as e:
        logging.error(f"ETL process failed: {e}")
        raise

if __name__ == "__main__":
    main()
