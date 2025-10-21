# producer.py
import pandas as pd, json, time
from kafka import KafkaProducer
from datetime import datetime, timezone

# Load and clean dataset
df = pd.read_csv("data/indexProcessed.csv")
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
if "closeusd" in df.columns:
    df.rename(columns={"closeusd": "close_usd"}, inplace=True)

# Normalize index labels
df["index"] = df["index"].astype(str).str.strip()

# Build per-index groups
index_groups = {idx: g.reset_index(drop=True) for idx, g in df.groupby("index")}
indexes = sorted(index_groups.keys())

print(f"[Producer] Found {len(indexes)} indexes:", indexes)

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

try:
    while True:
        stream_ts = datetime.now(timezone.utc).isoformat()
        # Emit one random row per index
        for idx in indexes:
            row = index_groups[idx].sample(1).iloc[0]
            message = {
                "stream_ts": stream_ts,   # same timestamp for all rows in this tick
                "index": row["index"],
                "date": pd.to_datetime(row["date"]).date().isoformat(),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "adj_close": float(row["adj_close"]),
                "volume": int(row["volume"]),
                "close_usd": float(row["close_usd"])
            }
            producer.send('stock_ticks', value=message)
            print("Sent:", message)
        producer.flush()
        time.sleep(1)  # control tick pace
except KeyboardInterrupt:
    print("Stopping producer.")