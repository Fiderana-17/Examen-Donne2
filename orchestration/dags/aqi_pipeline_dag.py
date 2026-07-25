"""
aqi_pipeline_dag.py — DAG Airflow : ingestion horaire -> reconstruction clean/ -> chargement warehouse.
A placer dans le dossier dags/ de votre instance Airflow (celle déjà en Docker sur Windows).

Secrets attendus (via Airflow Variables/Connections, PAS en dur) :
    OWM_API_KEY, DATABASE_URL
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "n7z-team",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}


def run_fetch_api():
    import subprocess
    subprocess.run(["python", "/opt/airflow/project/ingestion/fetch_api.py"], check=True)


def run_build_clean():
    import subprocess
    subprocess.run(["python", "/opt/airflow/project/transform/build_clean.py"], check=True)


def run_load_warehouse():
    import subprocess
    subprocess.run(["python", "/opt/airflow/project/warehouse/load_warehouse.py"], check=True)


with DAG(
    dag_id="aqi_pipeline",
    description="Collecte AQI horaire -> clean/ -> data warehouse",
    default_args=default_args,
    schedule_interval="@hourly",
    start_date=datetime(2026, 7, 17),
    catchup=False,
    tags=["donnees2", "aqi"],
) as dag:

    fetch_task = PythonOperator(
        task_id="fetch_api",
        python_callable=run_fetch_api,
    )

    clean_task = PythonOperator(
        task_id="build_clean",
        python_callable=run_build_clean,
    )

    load_task = PythonOperator(
        task_id="load_warehouse",
        python_callable=run_load_warehouse,
    )

    fetch_task >> clean_task >> load_task
