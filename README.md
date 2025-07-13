# NBA API Data Pipeline

A containerized data pipeline and dashboard for NBA player statistics, built with Apache Airflow, Docker, Python, and Streamlit.

---

## Tech Stack

- Python, pandas, duckdb, nba_api, pytest
- Apache Airflow (workflow orchestration)
- Docker & Docker Compose
- Streamlit (dashboard)
- AWS S3 for cloud storage

---

## Getting Started

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