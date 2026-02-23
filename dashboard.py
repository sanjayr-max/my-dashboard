import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Chat Performance Dashboard", layout="wide")
st.title("📊 Chat Performance Dashboard")

# ==============================
# LOAD DATA
# ==============================
@st.cache_data
def load_data():
    file_path = "daily_dump.xlsx"   # 🔁 CHANGE THIS TO YOUR FILE NAME
    df = pd.read_excel(file_path)
    return df

df = load_data()

# ==============================
# DATA CLEANING
# ==============================
df["Date"] = pd.to_datetime(df["Date"])

numeric_cols = [
    "Chat Count","FRT","Response Time","Resolution Time","Csat",
    "1 Count","2 Count","3 Count","4 Count","5 Count",
    "Total CSAT Count","login hrs (mins)","Reassign Chat count",
    "Quality Score","Call Count","Answered","Unanswered",
    "Csat Received %","Csat Missed %","Csat Difference","Call Difference"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.header("🔎 Filters")

min_date = df["Date"].min()
max_date = df["Date"].max()

date_range = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
    df = df[(df["Date"] >= pd.to_datetime(start_date)) &
            (df["Date"] <= pd.to_datetime(end_date))]

# Vendor Filter
vendor_list = ["All"] + sorted(df["Vendor"].dropna().unique().tolist())
selected_vendor = st.sidebar.selectbox("Select Vendor", vendor_list)

if selected_vendor != "All":
    df = df[df["Vendor"] == selected_vendor]

# Agent Filter (Dependent)
agent_list = ["All"] + sorted(df["Agent ID"].dropna().unique().tolist())
selected_agent = st.sidebar.selectbox("Select Agent", agent_list)

if selected_agent != "All":
    df = df[df["Agent ID"] == selected_agent]

# ==============================
# KPI SECTION
# ==============================
st.subheader("📌 Key Performance Indicators")

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Total Chats", int(df["Chat Count"].sum()))
k2.metric("Avg FRT", round(df["FRT"].mean(), 2))
k3.metric("Avg Resolution Time", round(df["Resolution Time"].mean(), 2))
k4.metric("Avg Response Time", round(df["Response Time"].mean(), 2))
k5.metric("Avg CSAT", round(df["Csat"].mean(), 2))

st.markdown("---")

# ==============================
# PERFORMANCE GRAPHS
# ==============================

st.subheader("📈 Agent Performance Overview")

agent_perf = df.groupby("Agent ID").agg({
    "Chat Count":"sum",
    "FRT":"mean",
    "Response Time":"mean",
    "Resolution Time":"mean",
    "Csat":"mean"
}).reset_index()

# Chats Taken
fig_chat = px.bar(agent_perf, x="Agent ID", y="Chat Count", text_auto=True, title="Chats Taken")
st.plotly_chart(fig_chat, use_container_width=True)

# FRT
fig_frt = px.bar(agent_perf, x="Agent ID", y="FRT", text_auto=True, title="Average FRT")
st.plotly_chart(fig_frt, use_container_width=True)

# Response Time
fig_resp = px.bar(agent_perf, x="Agent ID", y="Response Time", text_auto=True, title="Average Response Time")
st.plotly_chart(fig_resp, use_container_width=True)

# Resolution Time
fig_res = px.bar(agent_perf, x="Agent ID", y="Resolution Time", text_auto=True, title="Average Resolution Time")
st.plotly_chart(fig_res, use_container_width=True)

# CSAT
fig_csat = px.bar(agent_perf, x="Agent ID", y="Csat", text_auto=True, title="Average CSAT")
st.plotly_chart(fig_csat, use_container_width=True)

st.markdown("---")

# ==============================
# CHAT RECEIVED VS CSAT RECEIVED
# ==============================

st.subheader("💬 Chats Received vs Total CSAT Count")

csat_compare = df.groupby("Agent ID").agg({
    "Chat Count":"sum",
    "Total CSAT Count":"sum"
}).reset_index()

fig_compare = px.bar(
    csat_compare,
    x="Agent ID",
    y=["Chat Count", "Total CSAT Count"],
    barmode="group",
    title="Chats vs Total CSAT Count"
)

st.plotly_chart(fig_compare, use_container_width=True)

st.markdown("---")

# ==============================
# CALL PERFORMANCE
# ==============================

st.subheader("📞 Call Performance")

call_data = df.groupby("Agent ID")[["Answered","Unanswered"]].sum().reset_index()

fig_call = px.bar(
    call_data,
    x="Agent ID",
    y=["Answered","Unanswered"],
    barmode="group",
    title="Answered vs Unanswered Calls"
)

st.plotly_chart(fig_call, use_container_width=True)

st.markdown("---")

# ==============================
# QUALITY DISTRIBUTION
# ==============================

st.subheader("🎯 Quality Score Distribution")

fig_quality = px.histogram(df, x="Quality Score", nbins=20, title="Quality Score Distribution")
st.plotly_chart(fig_quality, use_container_width=True)

st.markdown("---")

# ==============================
# DOWNLOAD SECTION
# ==============================

st.subheader("⬇ Download Filtered Data")

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="filtered_dashboard_data.csv",
    mime="text/csv"
)

# ==============================
# DATA PREVIEW
# ==============================

st.subheader("📄 Filtered Data Preview")
st.dataframe(df, use_container_width=True)