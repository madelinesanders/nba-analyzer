# 🏀 NBA Analyzer

A containerized data pipeline and interactive dashboard for NBA player statistics analysis, built with **Apache Airflow**, **Docker**, **Python**, and **Streamlit**.

---

## 🚀 Features

- **Automated ETL pipeline**: Collects, processes, and validates NBA player stats from the NBA API.
- **Data storage**: Saves data in DuckDB, Parquet, and CSV formats.
- **Validation**: Runs automated tests on every ETL run.
- **Containerized**: Easy to run anywhere with Docker Compose.
- **Interactive dashboard**: Explore player and team stats with Streamlit.
- **Extensible**: Ready for S3 upload, more advanced analytics, and custom dashboards.

---

## 🛠️ Tech Stack

- Python, pandas, duckdb, nba_api, pytest
- Apache Airflow (workflow orchestration)
- Docker & Docker Compose
- Streamlit (dashboard)
- (Optional) AWS S3 for cloud storage

---

## ⚡ Quickstart

### 1. **Clone the repo**
```bash
git clone https://github.com/yourusername/nba-analyzer.git
cd nba-analyzer
```

### 2. **Set up environment variables**
- Copy `.env.example` to `.env` and fill in your secrets:
  ```bash
  cp .env.example .env
  ```
- Or create your own `.env` file with:
  ```
  AIRFLOW_ADMIN_PASSWORD=your_secure_password
  POSTGRES_PASSWORD=your_db_password
  AWS_ACCESS_KEY_ID=your_aws_key
  AWS_SECRET_ACCESS_KEY=your_aws_secret
  ```

### 3. **Start the pipeline**
```bash
docker-compose up -d
```
- Airflow UI: [http://localhost:8080](http://localhost:8080)
- Login: `madeline` / your `AIRFLOW_ADMIN_PASSWORD`

### 4. **Trigger the ETL DAG**
- In the Airflow UI, trigger the `nba_etl_dag` manually.

### 5. **Run the Streamlit Dashboard**
```bash
cd streamlit_app
streamlit run app.py
```
- Dashboard: [http://localhost:8501](http://localhost:8501)

---

## 🧪 Testing

- Data validation tests run automatically as part of the ETL.
- To run tests manually:
  ```bash
  docker-compose exec airflow pytest /opt/airflow/tests/test_data_validation.py
  ```

---

## 📁 Project Structure

```
nba-analyzer/
├── dags/                # Airflow DAGs
├── etl/                 # ETL scripts
├── tests/               # Data validation tests
├── streamlit_app/       # Streamlit dashboard
├── docker-compose.yaml  # Docker Compose config
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variables
└── README.md
```

---

## 🔒 Security & Best Practices

- **Never commit your real `.env` file or secrets.**
- Data files (`.csv`, `.parquet`, `.duckdb`) are gitignored and not tracked.
- For production, use strong passwords and secure your AWS credentials.

---

## 🙋‍♀️ About
