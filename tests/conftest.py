# conftest.py
import pytest
import pandas as pd

@pytest.fixture(scope="session")
def stats_df():
    return pd.read_parquet("stats_df_latest.parquet")
