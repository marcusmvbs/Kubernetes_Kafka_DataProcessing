from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
import subprocess

default_args = {
    'owner': 'airflow',
    # 'depends_on_past': False,
    # 'email_on_failure': False,
    # 'email_on_retry': False,
    'start_date': datetime(2024, 4, 20),
}

# def run_elt_script():
#     script_path = "elt/elt_script.py"
#     result = subprocess.run(["python", script_path],
#                             capture_output=True, text=True)
#     if result.returncode != 0:
#         raise Exception(f"Script failed with error: {result.stderr}")
#     else:
#         print(result.stdout)

dag = DAG('elt-script',
    default_args=default_args,
    description='Hello World DAG')

# t1 = PythonOperator(
#     task_id="run_elt_script",
#     python_callable=run_elt_script,
#     dag=dag
# )

t1 = KubernetesPodOperator(
    namespace="airflow",
    image="apache/airflow:2.8.3",
    task_id="run_elt_script",
    get_logs=True,
    dag=dag,
)