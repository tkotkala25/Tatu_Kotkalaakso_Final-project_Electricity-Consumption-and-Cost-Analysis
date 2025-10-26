import streamlit as st
import pandas as pd

# Page settings
st.set_page_config(page_title="Electricity Analysis Dashboard", layout="wide")
st.title("Electricity Consumption and Cost Analysis")

# Load data
df = pd.read_csv("Electricity_consumption_2015-2025.csv")
df_price = pd.read_csv("Electricity_price_2015-2025.csv", delimiter=';', decimal=',')

# Convert time columns
df['time'] = pd.to_datetime(df['time'])
df_price.rename(columns={df_price.columns[0]: 'timestamp'}, inplace=True)
df_price['timestamp'] = pd.to_datetime(df_price['timestamp'], format="%H:%M %m/%d/%Y", errors='coerce')

# Merge data
merged = pd.merge(df, df_price, left_on='time', right_on='timestamp', how='inner')
merged['Price'] = pd.to_numeric(merged['Price'], errors='coerce')
merged['Bill'] = (merged['Price'] / 100) * merged['kWh']
merged.dropna(inplace=True)

# Date range selector
start_date = st.date_input("Start Date", value=merged['time'].min().date())
end_date = st.date_input("End Date", value=merged['time'].max().date())

# Filter data
filtered = merged[(merged['time'].dt.date >= start_date) & (merged['time'].dt.date <= end_date)]

# Grouping selector
grouping = st.selectbox("Select Averaging Period", ["Daily", "Weekly", "Monthly"])
freq_map = {"Daily": "D", "Weekly": "W", "Monthly": "M"}
freq = freq_map[grouping]

# Aggregate data
grouped = filtered.resample(freq, on='time').agg({
    'kWh': 'sum',
    'Bill': 'sum',
    'Price': 'mean',
    'Temperature': 'mean'
})

# Summary metrics
total_kwh = filtered['kWh'].sum()
total_bill = filtered['Bill'].sum()
avg_price = filtered['Price'].mean()
avg_paid_price = (filtered['Bill'].sum() / filtered['kWh'].sum()) * 100

st.markdown("### Summary of Selected Period")
st.markdown(f"**Showing range:** {start_date} - {end_date}")
st.markdown(f"- **Total Consumption:** {total_kwh:.2f} kWh")
st.markdown(f"- **Total Bill:** {total_bill:.2f} €")
st.markdown(f"- **Average Hourly Price:** {avg_price:.2f} cents")
st.markdown(f"- **Average Paid Price:** {avg_paid_price:.2f} cents")

# Charts
st.markdown("### Electricity Consumption (kWh)")
st.line_chart(grouped['kWh'])

st.markdown("### Electricity Bill (€)")
st.line_chart(grouped['Bill'])

st.markdown("### Electricity Price (cents)")
st.line_chart(grouped['Price'])

st.markdown("### Temperature (°C)")
st.line_chart(grouped['Temperature'])

# Download button
csv = grouped.reset_index().to_csv(index=False).encode('utf-8')
st.download_button("Download Aggregated Data as CSV", data=csv, file_name="aggregated_electricity_data.csv", mime="text/csv")