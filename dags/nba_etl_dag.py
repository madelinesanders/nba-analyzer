from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess
import os

# DAG settings
default_args = {
    'owner': 'madeline',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'nba_etl_dag',
    default_args=default_args,
    description='NBA player stats ETL',
    catchup=False,
    tags=['nba', 'etl'],
    schedule_interval='0 13 * * 1'  # Every Monday at 13 UTC (9 AM EST)
)

def run_etl():
    import subprocess
    import os
    os.chdir('/opt/airflow')
    python_path = 'python'
    result = subprocess.run([python_path, 'etl/fetch_data.py'], capture_output=True, text=True)
    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)
    if result.returncode != 0:
        raise Exception(f"ETL script failed with exit code {result.returncode}")

# Create the task
etl_task = PythonOperator(
    task_id='run_etl',
    python_callable=run_etl,
    dag=dag
)