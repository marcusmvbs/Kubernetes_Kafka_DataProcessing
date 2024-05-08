from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
# from docker.types import Mount
# from airflow.operators.bash import BashOperator
# from airflow.providers.docker.operators.docker import DockerOperator
import subprocess

default_args = [
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
]

def run_elt_script():
    script_path = "/airflow/elt/elt_script.py"
    result = subprocess.run(["python", script_path],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Script failed with error: {result.stderr}")
    else:
        print(result.stdout)

dag = DAG(
    'elt_',
    default_args=default_args,
    description='An ELT workflow',
    schedule=timedelta(days=1),
    start_date=datetime(2024, 4, 20),
    catchup=False
)

t1 = PythonOperator(
    task_id="run_elt_script",
    python_callable=run_elt_script,
    dag=dag
)

t1

# t2 = PythonOperator(
#     task_id="load_save_data",
#     python_callable=load_save_data,
#     op_args=[t1.output],
#     dag=dag
# )

# t1 >> t2