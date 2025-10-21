# streamlit_app.py
import time
import streamlit as st
import psycopg2
import pandas as pd
import altair as alt
from datetime import datetime

st.set_page_config(page_title="StockPulse Live", layout="wide")

@st.cache_resource
def get_conn():
    return psycopg2.connect(
        host="localhost",
        dbname="stocks",
        user="postgres",
        password="password"
    )

def load_data():
    conn = get_conn()
    query = """
        SELECT stream_ts, index, close, volume
        FROM ticks_raw
        ORDER BY stream_ts DESC
        LIMIT 500
    """
    return pd.read_sql(query, conn)

# --- Main app ---
df = load_data()

tab1, tab2, tab3, tab4 = st.tabs(
    ["Raw Close", "% Change", "Rebased to 100", "Volume Share"]
)

with tab1:
    st.subheader("Raw Close Prices (absolute levels)")
    highlight = alt.selection_point(fields=["index"], on="mouseover")
    chart = alt.Chart(df).mark_line().encode(
        x="stream_ts:T",
        y="close:Q",
        color=alt.Color("index:N", scale=alt.Scale(scheme="category20")),
        opacity=alt.condition(highlight, alt.value(1), alt.value(0.2)),
        tooltip=["index", "close", "stream_ts"]
    ).add_params(highlight).interactive()
    st.altair_chart(chart, use_container_width=True)

with tab2:
    st.subheader("Percentage Change (relative moves)")
    df_pct = df.sort_values("stream_ts").copy()
    df_pct["pct_change"] = df_pct.groupby("index")["close"].pct_change() * 100
    chart = alt.Chart(df_pct).mark_line().encode(
        x="stream_ts:T",
        y="pct_change:Q",
        color=alt.Color("index:N", scale=alt.Scale(scheme="category20")),
        tooltip=["index", "pct_change", "stream_ts"]
    ).interactive()
    st.altair_chart(chart, use_container_width=True)

with tab3:
    st.subheader("Rebased to 100 (growth from baseline)")
    df_rebased = df.sort_values("stream_ts").copy()
    df_rebased["rebased"] = df_rebased.groupby("index")["close"].transform(
        lambda x: (x / x.iloc[0]) * 100
    )
    chart = alt.Chart(df_rebased).mark_line().encode(
        x="stream_ts:T",
        y="rebased:Q",
        color=alt.Color("index:N", scale=alt.Scale(scheme="category20")),
        tooltip=["index", "rebased", "stream_ts"]
    ).interactive()
    st.altair_chart(chart, use_container_width=True)

with tab4:
    st.subheader("Volume Share by Index (latest window)")
    volumes = df.groupby("index")["volume"].sum().reset_index()
    volumes["share"] = (volumes["volume"] / volumes["volume"].sum()) * 100
    chart = alt.Chart(volumes).mark_bar().encode(
        x="index:N",
        y="share:Q",
        color=alt.Color("index:N", scale=alt.Scale(scheme="category20")),
        tooltip=["index", "share"]
    )
    st.altair_chart(chart, use_container_width=True)

# Sidebar info
st.sidebar.success(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

# --- Auto-refresh every 5 seconds ---
time.sleep(5)
st.rerun()