from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

import sys
sys.path.append("/opt/airflow/app")

from extract_videos import run_extract
from transform_videos import run_transform


def extract():
    run_extract()

def transform():
    run_transform()


with DAG(
    dag_id="youtube_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False
) as dag:

    extract_task = PythonOperator(
        task_id="extract_videos",
        python_callable=extract
    )

    transform_task = PythonOperator(
        task_id="transform_videos",
        python_callable=transform
    )

    extract_task >> transform_task
