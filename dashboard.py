import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import requests

st.set_page_config(page_title="COSA OMEGA ASI – Threat Intel", layout="wide")
st.title("🛡️ COSA OMEGA ASI v15 – Threat Intelligence Dashboard")
st.caption(f"อัปเดตล่าสุด: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | ข้อมูลรวม APT + Emerging Attackers")

DB_PATH = "cosa_mesh_v15.db"
EVIDENCE_FOLDER = "mesh_evidence"
LOCAL_MODE = True  # ถ้า True ให้อ่าน local DB, ถ้า False ใช้ mock

def get_ip_location(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=2)
        if r.status_code == 200 and r.json().get('status') == 'success':
            return r.json().get('lat', 0), r.json().get('lon', 0)
    except:
        pass
    return 0, 0

@st.cache_data(ttl=300)
def load_data():
    if LOCAL_MODE:
        try:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query("""
                SELECT timestamp, ip, country, score, action, threat_type 
                FROM mesh_events 
                ORDER BY id DESC 
                LIMIT 2000
            """, conn)
            conn.close()
            return df
        except:
            st.warning("ไม่พบ DB ใช้ Mock Data แทน")
            return create_mock_data()
    else:
        return create_mock_data()

def create_mock_data():
    dates = [datetime.now() - timedelta(hours=i) for i in range(200)]
    return pd.DataFrame({
        "timestamp": dates,
        "ip": [f"192.168.{i}.{i}" for i in range(200)],
        "country": ["Russia","China","USA","Vietnam","India","Unknown"]*35,
        "score": [50,70,85,40,60,95]*35,
        "action": ["MONITORED","BLOCKED"]*100,
        "threat_type": ["apt","emerging","zero_day","scan"]*50
    })

df = load_data()

# anonymize ip
df['ip_short'] = df['ip'].apply(lambda x: x.split('.')[0] + '.***.***.***' if '.' in x else x)

# stats
col1, col2, col3, col4 = st.columns(4)
col1.metric("🌐 Malicious IPs", len(df['ip'].unique()))
col2.metric("🎯 Total Events", len(df))
col3.metric("🚫 BLOCKED (Thailand)", len(df[(df['action'] == 'BLOCKED') & (df['country'] == 'Thailand')]))
col4.metric("🔥 New Attackers", len(df[df['threat_type'] == 'emerging']))

# map (plotly scattergeo)
st.subheader("📍 ประเทศต้นทางของภัยคุกคาม")
country_counts = df['country'].value_counts().reset_index()
country_counts.columns = ['country', 'count']
fig = px.bar(country_counts.head(12), x='country', y='count', color='country')
st.plotly_chart(fig, use_container_width=True)

# trend
df['date'] = pd.to_datetime(df['timestamp']).dt.date
trend = df.groupby(['date', 'threat_type']).size().reset_index(name='count')
fig2 = px.line(trend, x='date', y='count', color='threat_type', title="แนวโน้ม APT vs Emerging vs Zero-day")
st.plotly_chart(fig2, use_container_width=True)

# risk distribution
fig3 = px.histogram(df, x='score', nbins=20, color='threat_type', title="คะแนนความเสี่ยง")
st.plotly_chart(fig3, use_container_width=True)

# recent events
st.subheader("📋 ตัวอย่างเหตุการณ์ (ไม่แสดง IP จริง)")
st.dataframe(df[['timestamp', 'ip_short', 'country', 'score', 'action', 'threat_type']].head(100), use_container_width=True)

st.caption("© 2026 Kriangkrai Khatsom | COSA OMEGA ASI | ข้อมูลเพื่อการป้องกันประเทศเท่านั้น")
