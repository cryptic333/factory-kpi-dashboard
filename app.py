import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Factory KPI Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("factory_events.csv", parse_dates=["timestamp"])
    return df

df = load_data()

st.title("🏭 Factory KPI Dashboard (Demo)")

# Filters
machines = ["All"] + sorted(df["machine"].unique().tolist())
pick_machine = st.selectbox("Machine", machines)

min_date = df["timestamp"].min().date()
max_date = df["timestamp"].max().date()
pick_dates = st.date_input("Date range", (min_date, max_date))

f = df.copy()
if pick_machine != "All":
    f = f[f["machine"] == pick_machine]

start_date, end_date = pick_dates
f = f[(f["timestamp"].dt.date >= start_date) & (f["timestamp"].dt.date <= end_date)]

# KPI calculations
total_units = int(f["units"].sum())
total_rejects = int(f["rejects"].sum())
good_units = total_units - total_rejects
scrap_rate = (total_rejects / total_units * 100) if total_units > 0 else 0

stop_events = f[f["status"] == "STOP"]
stop_count = int(stop_events.shape[0])

# Top stop reasons
reason_counts = stop_events["stop_reason"].value_counts()

# Layout
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Units", f"{total_units}")
c2.metric("Good Units", f"{good_units}")
c3.metric("Rejects", f"{total_rejects}")
c4.metric("Scrap Rate", f"{scrap_rate:.2f}%")

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Downtime (Stop Events) by Reason")
    fig = plt.figure()
    ax = fig.add_subplot(111)
    if len(reason_counts) > 0:
        ax.bar(reason_counts.index, reason_counts.values)
        ax.set_ylabel("Stop events")
        ax.set_xticks(range(len(reason_counts)))
        ax.set_xticklabels(reason_counts.index, rotation=30, ha="right")
    else:
        ax.text(0.5, 0.5, "No stop events in filter", ha="center")
        ax.set_axis_off()
    st.pyplot(fig)

with right:
    st.subheader("Units Produced Over Time")
    by_time = f.set_index("timestamp")["units"].resample("2h").sum()

    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111)
    ax2.plot(by_time.index, by_time.values)
    ax2.set_ylabel("Units (2-hour bins)")
    st.pyplot(fig2)

st.divider()

st.subheader("Raw Data (sample)")
st.dataframe(f.tail(50))
