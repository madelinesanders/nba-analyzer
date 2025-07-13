import pandas as pd
import time
import boto3
import duckdb
import logging
import pytest
import os
from datetime import datetime
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/airflow/etl/etl.log'),
        logging.StreamHandler()
    ]
)

def get_latest_stats_df():
    """Fetches active player career stats and returns concatenated DataFrame"""
    all_players = pd.DataFrame(players.get_players())
    player_ids = [row["id"] for _, row in all_players.iterrows() if row["is_active"]]
    dfs = []
    successful_fetches = 0
    failed_fetches = 0
    logging.info(f"Fetching data for {len(player_ids)} players...")

    for i, player_id in enumerate(player_ids):
        try:
            career = playercareerstats.PlayerCareerStats(player_id=player_id)
            career_df = career.get_data_frames()[0]
            player_name = all_players.loc[all_players["id"] == player_id, "full_name"].values[0]
            career_df["PLAYER_NAME"] = player_name
            dfs.append(career_df)
            successful_fetches += 1
            logging.info(f"✓ Added player {player_id} ({i+1}/{len(player_ids)}), {len(career_df)} rows")
            time.sleep(.3)
        except Exception as e:
            failed_fetches += 1
            logging.warning(f"Failed for player {player_id}: {e}")
            time.sleep(0.5)  # Short delay on failure

    logging.info(f"Fetch complete: {successful_fetches} successful, {failed_fetches} failed")
    
    if not dfs:
        raise ValueError("No data collected.")
    
    return pd.concat(dfs, ignore_index=True)


def main():
    logging.info("Starting NBA Data ETL")

    try:
        # Step 1: Collect data
        try:
            stats_df = get_latest_stats_df()
            logging.info(f"Collected {len(stats_df)} total records from API.")
        except Exception as e:
            logging.error(f"API data collection failed: {e}")
            logging.info("Attempting to use existing data...")
            if os.path.exists("stats_df_latest.parquet"):
                stats_df = pd.read_parquet("stats_df_latest.parquet")
                logging.info(f"Loaded {len(stats_df)} records from existing data.")
            else:
                raise Exception("No fallback available")

        # Step 2: Save locally
        timestamp = datetime.now().strftime('%Y%m%d')
        duckdb_path = f"stats_df_{timestamp}.duckdb"
        parquet_path = f"stats_df_{timestamp}.parquet"
        csv_path = f"stats_df_{timestamp}.csv"
        latest_parquet_path = "stats_df_latest.parquet" 

        # Save to DuckDB
        con = duckdb.connect(duckdb_path)
        con.execute("DROP TABLE IF EXISTS stats")
        con.execute("CREATE TABLE stats AS SELECT * FROM stats_df")
        con.close()
        logging.info("Saved data to DuckDB.")

        # Save to other formats
        stats_df.to_parquet(parquet_path, index=False)
        stats_df.to_parquet(latest_parquet_path, index=False)
        stats_df.to_csv(csv_path, index=False)
        logging.info("Saved data as Parquet and CSV.")

        # Step 3: Run validation tests (after saving)
        logging.info("Running data validation tests...")
        result = pytest.main(["/opt/airflow/tests/test_data_validation.py", "-q", "--tb=short", "-p", "no:warnings"])
        if result != 0:
            raise Exception("Data validation tests failed, aborting ETL.")
        logging.info("Data validation passed.")

        # Step 4: Upload to S3
        try:
            s3 = boto3.client(
                "s3",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
            )
            bucket = "nba-analyzer-data-madeline"

            s3.upload_file(duckdb_path, bucket, f"nba-data/stats_df_{timestamp}.duckdb")
            s3.upload_file(parquet_path, bucket, f"nba-data/stats_df_{timestamp}.parquet")
            s3.upload_file(csv_path, bucket, f"nba-data/stats_df_{timestamp}.csv")

            s3.upload_file(duckdb_path, bucket, "nba-data/latest/stats_df.duckdb")
            s3.upload_file(parquet_path, bucket, "nba-data/latest/stats_df.parquet")
            s3.upload_file(csv_path, bucket, "nba-data/latest/stats_df.csv")

            logging.info("Upload to S3 complete.")
        except Exception as s3_error:
            logging.warning(f"S3 upload failed (this is optional): {s3_error}")
            logging.info("Data files saved locally only.")

        logging.info("ETL Finished Successfully")

    except Exception as e:
        logging.error(f"ETL process failed: {e}")
        raise

if __name__ == "__main__":
    main()
