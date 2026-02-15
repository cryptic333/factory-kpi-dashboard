import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

st.set_page_config(layout="wide")
st.title("🏭 Smart Factory Performance Dashboard")

@st.cache_data
def load_data():
    df = pd.read_csv("factory_events.csv", parse_dates=["timestamp"])
    return df

df = load_data()

#  FILTER 
machines = ["All"] + sorted(df["machine"].unique())
selected_machine = st.selectbox("Select Machine", machines)

if selected_machine != "All":
    df = df[df["machine"] == selected_machine]

#  KPI CALCULATIONS
total_units = df["units"].sum()
total_rejects = df["rejects"].sum()
good_units = total_units - total_rejects

availability = (df["status"] == "RUN").mean() * 100
quality = (good_units / total_units * 100) if total_units > 0 else 0
performance = 90  # simulated stable performance %
oee = (availability/100) * (performance/100) * (quality/100) * 100

scrap_rate = (total_rejects / total_units * 100) if total_units > 0 else 0

#  KPI DISPLAY
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Units", int(total_units))
c2.metric("Scrap Rate %", f"{scrap_rate:.2f}")
c3.metric("Availability %", f"{availability:.1f}")
c4.metric("OEE %", f"{oee:.1f}")

st.divider()

#  PRODUCTION TREND 
st.subheader("Production Trend")

prod_trend = df.set_index("timestamp")["units"].resample("4H").sum()

fig1, ax1 = plt.subplots(figsize=(8,3))
ax1.plot(prod_trend.index, prod_trend.values)
ax1.set_ylabel("Units")

ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
ax1.xaxis.set_major_locator(mdates.AutoDateLocator())

plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig1)

# SCRAP TREND
st.subheader("Scrap Trend")

scrap_trend = df.set_index("timestamp")["rejects"].resample("4H").sum()

fig2, ax2 = plt.subplots(figsize=(8,3))
ax2.plot(scrap_trend.index, scrap_trend.values)
ax2.set_ylabel("Rejects")

ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
ax2.xaxis.set_major_locator(mdates.AutoDateLocator())

plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig2)

#MACHINE COMPARISON
st.subheader("Machine Output Comparison")

machine_output = df.groupby("machine")["units"].sum()

fig3, ax3 = plt.subplots(figsize=(6,3))
ax3.bar(machine_output.index, machine_output.values)
ax3.set_ylabel("Total Units")
plt.tight_layout()
st.pyplot(fig3)

#  SCRAP RATE BY MACHINE
st.subheader("Scrap Rate by Machine")

scrap_machine = df.groupby("machine").apply(
    lambda x: (x["rejects"].sum() / x["units"].sum()) * 100 if x["units"].sum() > 0 else 0
)

fig4, ax4 = plt.subplots(figsize=(6,3))
ax4.bar(scrap_machine.index, scrap_machine.values)
ax4.set_ylabel("Scrap Rate %")
plt.tight_layout()
st.pyplot(fig4)

# DOWNTIME BREAKDOWN
st.subheader("Downtime Breakdown")

stop_data = df[df["status"] == "STOP"]
reason_counts = stop_data["stop_reason"].value_counts()

fig5, ax5 = plt.subplots(figsize=(6,3))
ax5.pie(reason_counts, labels=reason_counts.index, autopct="%1.1f%%")
plt.tight_layout()
st.pyplot(fig5)

# HEATMAP
st.subheader("Hourly Production Heatmap")

df["hour"] = df["timestamp"].dt.hour
heatmap_data = df.groupby(["machine", "hour"])["units"].sum().unstack(fill_value=0)

fig6, ax6 = plt.subplots(figsize=(10,4))

c = ax6.imshow(heatmap_data.values, aspect="auto")

ax6.set_xticks(range(24))
ax6.set_xticklabels(range(24))
ax6.set_yticks(range(len(heatmap_data.index)))
ax6.set_yticklabels(heatmap_data.index)

ax6.set_xlabel("Hour of Day")
ax6.set_ylabel("Machine")

fig6.colorbar(c, ax=ax6)

plt.tight_layout()
st.pyplot(fig6)

# DAILY SUMMARY
st.subheader("Daily Summary")

daily_summary = df.set_index("timestamp").resample("D").agg({
    "units": "sum",
    "rejects": "sum"
})

daily_summary["scrap_rate_%"] = (
    daily_summary["rejects"] / daily_summary["units"]
) * 100

st.dataframe(daily_summary)
