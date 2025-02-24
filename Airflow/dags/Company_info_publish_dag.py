from airflow import DAG
from airflow.providers.google.cloud.operators.cloud_run import CloudRunExecuteJobOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import pytz


default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retry_delay': timedelta(minutes=5)
}

def branch_stock_job(**kwargs):
    eastern = pytz.timezone('US/Eastern')
    exec_date = kwargs['execution_date'].astimezone(eastern)
    if exec_date.weekday() < 5:
        market_start = datetime.strptime("09:30", "%H:%M").time()
        market_end = datetime.strptime("16:00", "%H:%M").time()
        if market_start <= exec_date.time() < market_end:
            return "execute_stock_job"
    return "skip_stock_job"

def branch_company_job(**kwargs):
    eastern = pytz.timezone('US/Eastern')
    exec_date = kwargs['execution_date'].astimezone(eastern)
    now_eastern = datetime.now(eastern)
    # Run only on weekdays and at 10:00 AM (allowing a 2-minute window)
    if exec_date.weekday() < 5 and exec_date.hour == 9 and exec_date.minute < 32:
        return "execute_company_job"
    return "skip_company_job"


with DAG(
    'combined_cloud_run_jobs_dag',
    default_args=default_args,
    schedule_interval='*/10 * * * *',  # DAG triggers every 10 minutes
    catchup=False,
    description="Run company info job at ~10 AM ET (M-F) and stock quotes job every 10 mins during market hours"
) as dag:

    # Branch for stock quotes job
    branch_stock = BranchPythonOperator(
        task_id='branch_stock',
        python_callable=branch_stock_job,
    )

    # Branch for company info job
    branch_company = BranchPythonOperator(
        task_id='branch_company',
        python_callable=branch_company_job,
    )

    # Cloud Run operator for the stock quotes job
    execute_stock_job = CloudRunExecuteJobOperator(
        task_id='execute_stock_job',
        project_id='stock-data-project-449518',
        region='us-central1',
        job_name='publish-stock-quotes',   # Replace with your actual job name
        gcp_conn_id='google_cloud_default'
    )

    # Dummy operator to skip the stock quotes job
    skip_stock_job = EmptyOperator(task_id='skip_stock_job')

    # Cloud Run operator for the company info job
    execute_company_job = CloudRunExecuteJobOperator(
        task_id='execute_company_job',
        project_id='stock-data-project-449518',
        region='us-central1',
        job_name='publish-company',         # Replace with your actual job name
        gcp_conn_id='google_cloud_default'
    )

    # Dummy operator to skip the company info job
    skip_company_job = EmptyOperator(task_id='skip_company_job')

    
    branch_stock >> [execute_stock_job, skip_stock_job]
    branch_company >> [execute_company_job, skip_company_job]