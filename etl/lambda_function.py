import pandas as pd
import time
import boto3
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players

def lambda_handler(event, context):
    # Get names, id's, and active status of all players
    all_players = pd.DataFrame(players.get_players())

    # Filter active players
    player_ids = [row["id"] for index, row in all_players.iterrows() if row["is_active"] == True]

    # Collect career stats
    dfs = []
    for player_id in player_ids[:10]:
        try:
            career = playercareerstats.PlayerCareerStats(player_id=player_id)
            career_df = career.get_data_frames()[0]
            dfs.append(career_df)
            time.sleep(0.1)  # to avoid rate limiting, play around with time
        except Exception as e:
            print(f"Error with player {player_id}: {e}")

    if not dfs:
        return {"statusCode": 500, "body": "No data collected"}

    # Combine the dataframes of each player
    stats_df = pd.concat(dfs, ignore_index=True)

    # Save to temp file (only location Lambda can write to)
    file_path = "/tmp/stats_df.csv"
    stats_df.to_csv(file_path, index=False)

    # Upload to S3
    s3 = boto3.client("s3")
    bucket_name = "nba-analyzer-data-madeline"
    s3_key = "nba-data/stats_df.csv"

    try:
        s3.upload_file(file_path, bucket_name, s3_key)
        print(f"File uploaded to s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print(f"Upload failed: {e}")
        return {"statusCode": 500, "body": "Upload failed"}

    return {"statusCode": 200, "body": "Upload successful"}
# temp test comment
