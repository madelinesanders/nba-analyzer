import pytest

@pytest.fixture(scope="session")
def stats_df():
    from etl.fetch_data import get_latest_stats_df
    return get_latest_stats_df()
