import streamlit as st
import duckdb
import os

# Config
PARQUET_URL = "s3://nba-analyzer-data-madeline/nba-data/latest/stats_df.parquet"

@st.cache_data
def load_data():
    con = duckdb.connect()
    # Install and load httpfs plugin
    try:
        con.execute("INSTALL httpfs;")
    except Exception:
        pass  # Already installed
    con.execute("LOAD httpfs;")
    # Set AWS credentials
    con.execute("SET s3_region='us-east-2';")
    con.execute(f"SET s3_access_key_id='{os.environ.get('AWS_ACCESS_KEY_ID', '')}';")
    con.execute(f"SET s3_secret_access_key='{os.environ.get('AWS_SECRET_ACCESS_KEY', '')}';")
    # Query data directly from S3
    df = con.execute(f"SELECT * FROM read_parquet('{PARQUET_URL}')").df()
    return df

st.title("🏀 NBA Player Stats Dashboard")
st.caption("Powered by DuckDB + Streamlit + S3")

try:
    df = load_data()
    st.subheader("Dataset Preview")
    st.dataframe(df.head(50))
    st.markdown(f"**Total Records:** {len(df)}")
except Exception as e:
    st.error(f"Failed to load data: {e}")