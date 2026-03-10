from airflow import DAG
from datetime import datetime, timedelta
from airflow.providers.standard.operators.bash import BashOperator

start_date = datetime(2026, 2, 11)

default_args = {
    "owner": "airflow",
    "start_date": start_date,
    "retries": 1,
    "retry_delay": timedelta(seconds=5),
}

with DAG("my_dag", default_args=default_args, schedule="@daily", catchup=False) as dag:
    t0 = BashOperator(
        task_id="ls_data",
        bash_command='echo "Hello! I am task0"',
        retries=2,
        retry_delay=timedelta(seconds=15),
    )

    t1 = BashOperator(
        task_id="download_data",
        bash_command='echo "Hello! I am task1"',
        retries=2,
        retry_delay=timedelta(seconds=15),
    )

    t2 = BashOperator(
        task_id="check_file_exists",
        bash_command='echo "Hello! I am task3"',
        retries=2,
        retry_delay=timedelta(seconds=15),
    )

    t0 >> t1 >> t2
