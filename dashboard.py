git add dashboard.py
git commit -m "Add C2-style dashboard"
git push origin mainimport streamlit as st
import pandas as pd
import plotly.express as px
import random
import time
from datetime import datetime, timedelta

st.set_page_config(page_title="COSA OMEGA ASI – LIVE THREAT", layout="wide")

# Custom CSS (ธีม黑客)
st.markdown("""
<style>
    .stApp { background-color: #0a0f1a; }
    .css-1v3fvcr, .css-1v0mbdj { color: #00f2ff; }
    .stMetric { background-color: #121826; border-left: 4px solid #00f2ff; }
    .reportview-container .main .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ COSA OMEGA ASI v15 – LIVE THREAT PANEL")
st.caption(f"อัปเดตล่าสุด: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | มุมมองสำหรับผู้ตัดสินใจ")

# ========== SESSION STATE (จำลอง memory) ==========
if 'event_count' not in st.session_state:
    st.session_state.event_count = 1245
if 'new_threats' not in st.session_state:
    st.session_state.new_threats = 0

# สุ่มเพิ่ม event (จำลองการโจมตี)
if st.button("🔄 Refresh / Rescan", type="primary"):
    new = random.randint(1, 15)
    st.session_state.event_count += new
    st.session_state.new_threats = new
    st.rerun()

# ========== METRICS ==========
col1, col2, col3, col4 = st.columns(4)
col1.metric("🌐 TOTAL MALICIOUS IPs", f"{st.session_state.event_count:,}", delta="+12" if st.session_state.new_threats else None)
col2.metric("🚫 BLOCKED (Thailand)", "0", delta="All threats external")
col3.metric("🔥 NEW ATTACKERS (24h)", f"{st.session_state.new_threats}", delta="⚠️ Monitor")
col4.metric("⚡ ACTIVE PROBES", f"{random.randint(3,12)}", delta="-2")

# ========== ALERT AREA (กรณีมีภัยใหม่) ==========
if st.session_state.new_threats > 0:
    st.warning(f"🚨 **NEW THREATS DETECTED!** {st.session_state.new_threats} suspicious IPs observed in last scan.", icon="⚠️")

# ========== GRAPH (Bar chart ประเทศ) ==========
st.subheader("📍 TOP ATTACKER COUNTRIES (Today)")
countries = ["USA", "Russia", "China", "Vietnam", "India", "Pakistan", "Unknown"]
counts = [random.randint(5, 50) for _ in countries]
df_country = pd.DataFrame({"Country": countries, "Probes": counts})
fig = px.bar(df_country, x="Country", y="Probes", color="Country", text="Probes")
st.plotly_chart(fig, use_container_width=True)

# ========== SIMPLE LOG (เหมือน C2) ==========
st.subheader("📡 RECENT THREAT LOGS (auto-refresh)")
log_placeholder = st.empty()

# เปลี่ยน logs ทุกครั้งที่ refresh หรือ rerun
logs = [
    f"[{datetime.now().strftime('%H:%M:%S')}] SCAN: 5.188.86.123 (RU) → Port scan",
    f"[{datetime.now().strftime('%H:%M:%S')}] ALERT: 45.56.162.192 (US) → C2 beacon",
    f"[{datetime.now().strftime('%H:%M:%S')}] INFO: 113.212.70.104 (ID) → Brute force",
    f"[{datetime.now().strftime('%H:%M:%S')}] MITIGATED: 222.222.254.165 (CN) → Blocked",
]
log_placeholder.code("\n".join(logs), language="bash")

st.info("💡 **TIP:** กด 'Refresh' เพื่อจำลองการตรวจจับรอบใหม่ → 外人เห็นแค่ภาพ ไม่เห็นข้อมูลจริง", icon="💡")
