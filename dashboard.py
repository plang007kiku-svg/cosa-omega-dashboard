import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="COSA OMEGA ASI – Threat Intel", layout="wide")
st.title("🛡️ COSA OMEGA ASI v15 – Threat Intelligence Dashboard")
st.caption(f"อัปเดตล่าสุด: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | ข้อมูลรวม APT + Emerging Attackers")

@st.cache_data(ttl=300)
def load_data():
    # Mock data (เหมือนเดิม แต่ตรวจสอบความยาว)
    dates = [datetime.now() - timedelta(hours=i) for i in range(200)]
    countries = ["Russia","China","USA","Vietnam","India","Unknown"] * 35  # 210 ตัว → เอาแค่ 200
    countries = countries[:200]
    scores = [50,70,85,40,60,95] * 35
    scores = scores[:200]
    actions = ["MONITORED","BLOCKED"] * 100
    threat_types = ["apt","emerging","zero_day","scan"] * 50
    
    return pd.DataFrame({
        "timestamp": dates,
        "ip": [f"192.168.{i%256}.{i%256}" for i in range(200)],
        "country": countries,
        "score": scores,
        "action": actions,
        "threat_type": threat_types
    })

df = load_data()
df['ip_short'] = df['ip'].apply(lambda x: x.split('.')[0] + '.***.***.***')

col1, col2, col3, col4 = st.columns(4)
col1.metric("🌐 Malicious IPs", len(df['ip'].unique()))
col2.metric("🎯 Total Events", len(df))
col3.metric("🚫 BLOCKED (Thailand)", len(df[(df['action'] == 'BLOCKED') & (df['country'] == 'Thailand')]))
col4.metric("🔥 New Attackers", len(df[df['threat_type'] == 'emerging']))

st.subheader("📍 ประเทศต้นทางของภัยคุกคาม")
country_counts = df['country'].value_counts().reset_index()
country_counts.columns = ['country', 'count']
fig = px.bar(country_counts.head(12), x='country', y='count', color='country')
st.plotly_chart(fig, use_container_width=True)

df['date'] = pd.to_datetime(df['timestamp']).dt.date
trend = df.groupby(['date', 'threat_type']).size().reset_index(name='count')
fig2 = px.line(trend, x='date', y='count', color='threat_type', title="แนวโน้ม APT vs Emerging vs Zero-day")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("📋 ตัวอย่างเหตุการณ์ (ไม่แสดง IP จริง)")
st.dataframe(df[['timestamp', 'ip_short', 'country', 'score', 'action', 'threat_type']].head(100), use_container_width=True)

st.caption("© 2026 Kriangkrai Khatsom | COSA OMEGA ASI | ข้อมูลเพื่อป้องกันประเทศเท่านั้น")

