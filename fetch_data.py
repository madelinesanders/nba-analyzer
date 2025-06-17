import pandas as pd
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
import time

all_players = pd.DataFrame(players.get_players())


player_ids = []


for index, row in all_players.iterrows():
    if row["is_active"] == True:
        player_ids.append(row["id"])

dfs = []
for id in player_ids[:10]:
    try:
        career = playercareerstats.PlayerCareerStats(player_id=id)
        career_df = career.get_data_frames()[0]
        dfs.append(career_df)
        print(f"Successfully added player {id}")
    except Exception as e:
        print(f"Error with player {id}: {e}")

stats_df = pd.concat(dfs, ignore_index=True)
stats_df.drop(columns=["Unnamed: 0", inplace=True])

stats_df.to_csv("stats_df.csv")

print(stats_df.head())

