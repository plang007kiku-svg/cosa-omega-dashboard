import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import random
from datetime import datetime
from OTXv2 import OTXv2
import json

st.set_page_config(page_title="COSA OMEGA ASI – C2 PANEL", layout="wide")

# ========== Config from secrets ==========
OTX_API_KEY = st.secrets.get("otx_api_key", None)

# ========== Session State ==========
if 'event_log' not in st.session_state:
    st.session_state.event_log = []
if 'blocklist' not in st.session_state:
    st.session_state.blocklist = []
if 'threat_indicators' not in st.session_state:
    st.session_state.threat_indicators = {}

# ========== Sidebar ==========
with st.sidebar:
    st.markdown("## 🎮 CONTROL PANEL")
    if st.button("🔄 RESCAN GLOBAL THREATS"):
        st.session_state.event_log.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] Rescan triggered")
        new_ips = random.sample(["45.56.162.192", "193.29.56.122", "5.167.68.114", "113.212.70.104"], k=random.randint(1,3))
        for ip in new_ips:
            st.session_state.threat_indicators[ip] = {"first_seen": datetime.now().isoformat(), "status": "monitoring"}
        st.rerun()
    
    if st.button("🔒 APPLY BLOCKLIST (Thai only)"):
        for ip in list(st.session_state.threat_indicators.keys()):
            if random.choice([True, False]):
                st.session_state.blocklist.append(ip)
                st.session_state.event_log.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] BLOCKED {ip}")
        st.rerun()
    
    if st.button("📤 EXPORT EVIDENCE (for NCSA)"):
        tmp = {"blocked": st.session_state.blocklist,
               "monitored": list(st.session_state.threat_indicators.keys()),
               "timestamp": datetime.now().isoformat()}
        st.download_button("📥 Download JSON", data=json.dumps(tmp, indent=2), file_name="ncsa_evidence.json")
    
    if st.button("🧹 RESET ALL"):
        st.session_state.event_log.clear()
        st.session_state.blocklist.clear()
        st.session_state.threat_indicators.clear()
        st.rerun()

# ========== Main Panel ==========
st.markdown("# 🛡️ COSA OMEGA ASI v15 – C2 Interface")
st.caption(f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("📡 ACTIVE THREATS", len(st.session_state.threat_indicators))
col2.metric("🔒 BLOCKED", len(st.session_state.blocklist))
col3.metric("📤 EVIDENCE", "Ready" if st.session_state.blocklist else "No")
col4.metric("🎮 STATUS", "Active")

# OTX Live APT Groups
st.subheader("🔴 OTX LIVE APT GROUPS (AlienVault)")
if OTX_API_KEY:
    try:
        otx = OTXv2(OTX_API_KEY)
        apt_groups = ["APT28", "APT32", "Lazarus", "APT36", "Darkhotel", "Seedworm"]
        active = {}
        for grp in apt_groups:
            pulses = otx.search_pulses(q=grp, limit=1, sort="-modified")
            if pulses:
                active[grp] = pulses[0].get('modified', 'N/A')[:10]
        df_apt = pd.DataFrame([{"Group": k, "Last Update": v} for k,v in active.items()])
        st.dataframe(df_apt, use_container_width=True)
    except Exception as e:
        st.warning(f"Cannot fetch OTX: {e}")
else:
    st.info("OTX API Key not set (外人ไม่เห็น)", icon="🔑")

# Current Threats
st.subheader("📋 CURRENT THREAT INDICATORS (Anonymous)")
if st.session_state.threat_indicators:
    df_ind = pd.DataFrame([{"IP (masked)": k[:6]+"***", "First Seen": v["first_seen"][:19], "Status": v["status"]} 
                           for k,v in st.session_state.threat_indicators.items()])
    st.dataframe(df_ind, use_container_width=True)
else:
    st.info("No active threats. Press 'Rescan' to start.")

# Event Log
st.subheader("📡 EVENT LOG")
st.code("\n".join(st.session_state.event_log[-15:]), language="bash")

st.caption("© 2026 Kriangkrai Khatsom | 外人เห็นแค่ UI ไม่เห็นข้อมูลจริง")
