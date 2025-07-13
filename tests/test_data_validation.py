import pytest

REQUIRED_COLUMNS = [
    "PLAYER_ID", "SEASON_ID", "TEAM_ID", "PLAYER_NAME", "PTS", "AST", "REB", "GP"
]

def test_required_columns_present(stats_df):
    for col in REQUIRED_COLUMNS:
        assert col in stats_df.columns, f"Missing required column: {col}"

def test_no_nulls_in_critical_columns(stats_df):
    for col in REQUIRED_COLUMNS:
        assert stats_df[col].isnull().sum() == 0, f"Column {col} contains nulls"

def test_points_are_non_negative(stats_df):
    assert (stats_df["PTS"] >= 0).all(), "PTS column has negative values"

def test_games_played_valid(stats_df):
    assert stats_df["GP"].ge(0).all(), "GP column has invalid values"