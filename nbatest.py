import pandas as pd
from nba_api.stats.static import players
all_players = pd.DataFrame(players.get_players())

print(all_players.head(10))