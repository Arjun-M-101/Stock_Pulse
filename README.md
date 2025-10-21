# 📈 StockPulse – Real‑Time Data Engineering Pipeline (Streaming)

## 🚀 Overview
**StockPulse** is a **real‑time data engineering pipeline** that simulates live stock index ticks and processes them end‑to‑end.  

It demonstrates a **modern streaming architecture** using:

- **Kafka** → Message broker for real‑time ingestion  
- **Apache Spark Structured Streaming** → Scalable stream processing & ETL  
- **Postgres** → Serving layer for analytics  
- **Parquet Data Lake** → Partitioned storage for historical queries  
- **Apache Airflow (3.x)** → Orchestration & scheduling  
- **Streamlit + Altair** → Interactive BI dashboard  

The pipeline ingests simulated stock index data, enriches it with derived metrics, stores it in both **Postgres** and **Parquet**, and visualizes it in real‑time.

---

## 🏗️ Architecture

```
[ indexProcessed.csv ]
        │
        ▼
 [ Kafka Producer ]  --->  [ Kafka Topic: stock_ticks ]  --->  [ Spark Structured Streaming Consumer ]
                                                                 │
                                                                 ├──> [ Parquet Data Lake (partitioned by index/date) ]
                                                                 │
                                                                 └──> [ Postgres DB (ticks_raw table) ]
                                                                                   │
                                                                                   ▼
                                                                       [ Streamlit Dashboard ]
                                                                                   │
                                                                                   ▼
                                                                         Interactive Visuals
                                                                                   │
                                                                                   ▼
                                                                         [ Airflow DAG Orchestration ]
```

---

## 📂 Project Structure

```text
stock_pulse/
│
├── airflow/                      # Airflow home (local)
│   ├── dags/
│   │   └── stock_pipeline_dag.py # Airflow DAG definition
│   ├── logs/                     # Airflow logs
│   ├── airflow.cfg               # Airflow config
│   └── airflow.db                # Airflow metadata DB
│
├── chk/                          # Spark checkpoints
│   ├── parquet/
│   └── postgres/
│
├── consumer/
│   └── consumer.py               # Spark Structured Streaming consumer
│
├── data/
│   └── indexProcessed.csv        # Input dataset for producer
│
├── lake/
│   └── parquet/                  # Partitioned parquet sink (index/date)
│
├── postgres/
│   └── init.sql                  # DB init script (optional)
│
├── producer/
│   └── producer.py               # Kafka producer (simulated ticks)
│
├── clear_outputs.py              # Utility to clear outputs/checkpoints
├── requirements-lock.txt         # Pinned dependencies
├── streamlit_app.py              # Streamlit + Altair dashboard
└── venv/                         # Python virtual environment (local)
```

---

## 🛠️ Prerequisites & Installation

### System Packages

- **Python 3.10+**
  ```bash
  sudo apt update
  sudo apt install -y python3 python3-venv python3-dev
  ```

- **Java (JDK 11+)** → required for PySpark
  ```bash
  sudo apt install -y openjdk-11-jdk
  java -version
  ```

- **Apache Spark**
  ```bash
  wget https://downloads.apache.org/spark/spark-3.4.1/spark-3.4.1-bin-hadoop3.tgz
  tar xvf spark-3.4.1-bin-hadoop3.tgz
  mv spark-3.4.1-bin-hadoop3 ~/spark
  export SPARK_HOME=~/spark
  export PATH=$SPARK_HOME/bin:$PATH
  spark-shell --version
  ```

- **Kafka**
  ```bash
  wget https://downloads.apache.org/kafka/3.6.0/kafka_2.13-3.6.0.tgz
  tar -xzf kafka_2.13-3.6.0.tgz
  mv kafka_2.13-3.6.0 ~/kafka
  ```

  Start services in separate terminals:
  ```bash
  ~/kafka/bin/zookeeper-server-start.sh ~/kafka/config/zookeeper.properties
  ~/kafka/bin/kafka-server-start.sh ~/kafka/config/server.properties
  ```

- **Postgres**
  ```bash
  sudo apt install -y postgresql postgresql-contrib libpq-dev
  sudo systemctl start postgresql
  ```

  Create DB:
  ```sql
  CREATE DATABASE stocks;
  \c stocks
  ```

  Create Table:
  ```sql
  -- create fresh table
  CREATE TABLE ticks_raw (
    stream_ts TIMESTAMPTZ NOT NULL,
    date DATE NOT NULL,
    index TEXT NOT NULL,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC NOT NULL,
    adj_close NUMERIC,
    volume BIGINT NOT NULL,
    close_usd NUMERIC,
    trade_value NUMERIC
  );
  ```
  
- **Airflow (3.x)**
  ```bash
  pip install apache-airflow
  airflow db migrate
  airflow standalone
  ```

---

## ⚙️ Setup Instructions

### Clone repo
```bash
git clone https://github.com/Arjun-M-101/StockPulse.git
cd stock_pulse
```

### Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-lock.txt
```

### Start Kafka topic
```bash
~/kafka/bin/kafka-topics.sh --create --topic stock_ticks --bootstrap-server localhost:9092
```

### Run Producer
```bash
python producer/producer.py
```

### Run Consumer (Spark)
```bash
$SPARK_HOME/bin/spark-submit \
  --master local[*] \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,org.postgresql:postgresql:42.7.4 \
  consumer/consumer.py
```

### Trigger Airflow DAG
In Airflow UI → enable and trigger `stockpulse_pipeline`.

### Launch Dashboard
```bash
streamlit run streamlit_app.py
```

### Reset Outputs (optional)
```bash
python clear_outputs.py
```

- Clears: `lake/parquet` contents and Spark checkpoint directories (`chk/parquet`, `chk/postgres`)  
- Restores: `.gitkeep` to keep folders tracked by Git  

---

## 📊 Dashboard Features

- **Raw Close Prices** → Line chart of absolute price levels  
- **% Change** → Relative moves per index  
- **Rebased to 100** → Growth from baseline  
- **Volume Share** → Market share by traded volume  

Auto‑refreshes every 5 seconds for live updates.

---

## 🔄 Data Flow

### **Producer**
- Reads `indexProcessed.csv`  
- Emits **1 row per index per tick** with synchronized timestamp  
- Publishes to Kafka topic `stock_ticks`

### **Consumer (Spark)**
- Reads from Kafka in streaming mode  
- Parses JSON → applies schema  
- Adds derived column: `trade_value = close * volume`  
- Writes to:
  - **Parquet** (partitioned by index/date)  
  - **Postgres** (`ticks_raw` table)

### **Airflow DAG**
- Orchestrates Spark consumer job  
- Can be extended for retries, alerts, and scheduling

### **Dashboard**
- Connects to Postgres  
- Queries latest 500 ticks  
- Provides interactive Altair visualizations

### **Clear Outputs Utility**
- `clear_outputs.py` wipes **lake/parquet** and **chk/** directories  
- Restores `.gitkeep` to preserve folder structure  
- Useful for reproducibility and fresh pipeline runs

---

## ✅ Key Takeaways

- Demonstrates **real‑time streaming pipeline** with Kafka + Spark  
- Dual sink: **Parquet (historical)** + **Postgres (serving)**  
- **Airflow DAG** for orchestration  
- **Streamlit dashboard** for recruiter‑friendly visualization  
- **Clear outputs utility** for reproducible resets  
- Fully reproducible locally, but cloud‑ready (S3, EMR, MWAA, RDS/Redshift)

---

## ⚖️ Trade‑offs & Design Decisions

- **Kafka vs. File Watcher** → Kafka chosen for scalability & replayability  
- **Postgres vs. Data Warehouse** → Postgres is lightweight for local dev; Redshift/Snowflake for production  
- **Parquet partitioning** → Enables efficient historical queries  
- **Airflow standalone** → Simple for demo; MWAA/K8s for production  
- **Streamlit** → Fast prototyping; Superset/Tableau for enterprise BI  
- **Checkpoints clearing** → Safe in dev to replay from earliest; avoid in prod to prevent duplicates  

---