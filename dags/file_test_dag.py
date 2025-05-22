from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

def write_test_file():
    viz_dir = '/opt/airflow/data/visualizations'
    os.makedirs(viz_dir, exist_ok=True)
    
    with open(f'{viz_dir}/test_from_dag.html', 'w') as f:
        f.write(f'<html><body><h1>Test from DAG</h1><p>Created at {datetime.now()}</p></body></html>')
    
    return 'File written successfully'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 0,
}

dag = DAG(
    'file_test_dag',
    default_args=default_args,
    description='Test file writing',
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
)

task = PythonOperator(
    task_id='write_test_file',
    python_callable=write_test_file,
    dag=dag,
)
