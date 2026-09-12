from airflow.sdk import dag, task
import pendulum


@dag(
    dag_id="hola_airflow",
    schedule=None,
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    tags=["learning"],
)
def hello_airflow():

    @task
    def start():
        print("Starting my first Airflow DAG!")

    @task
    def process():
        print("Processing some imaginary data...")

    @task
    def finish():
        print("Everything finished successfully!")

    start() >> process() >> finish()


hello_airflow()