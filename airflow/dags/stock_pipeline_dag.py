# stock_pipeline_dag.py
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
import pendulum, os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
default_args = {"owner": "arjun", "retries": 0}

with DAG(
    dag_id="stockpulse_pipeline",
    default_args=default_args,
    description="StockPulse: Kafka → Spark → Postgres + Parquet",
    start_date=pendulum.now().subtract(days=1),
    schedule=None,
    catchup=False
) as dag:

    spark_consumer = BashOperator(
        task_id="spark_consumer",
        bash_command="$SPARK_HOME/bin/spark-submit "
                    "--master local[*] "
                    "--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,"
                    "org.postgresql:postgresql:42.7.4 "
                    "/home/arjun/stock_pulse/consumer/consumer.py"
    )