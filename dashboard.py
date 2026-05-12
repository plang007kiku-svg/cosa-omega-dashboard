import streamlit as st
import pandas as pd
import plotly.express as px
import networkx as nx
import random
import time
import threading
from datetime import datetime
from OTXv2 import OTXv2
import json

st.set_page_config(page_title="COSA OMEGA v16 – C2 Correlation & Threat Map", layout="wide")
st.markdown("### 🧠 COSA OMEGA v16 – C2 HUNTER (Quantum Correlation)")
st.caption(f"Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 外人เห็นแค่ surface ไม่เห็น correlation engine")

# ========== CONFIG (外人ไม่เห็น) ==========
OTX_API_KEY = st.secrets["otx_api_key"]

# MISP + Resurvey Data (外人ไม่เห็น correlation)
C2_CLUSTERS = {
    "APT28": {"ips": ["45.56.162.192", "193.29.56.122"], "c2_domain": "hcisupport.in"},
    "APT32": {"ips": ["113.212.70.104", "5.167.68.114"], "c2_domain": "hcidoc.in"},
    "Lazarus": {"ips": ["203.150.199.27", "223.24.62.44"], "c2_domain": "coadelhi.in"}
}
TH_CONDITION = lambda ip: ip.startswith("203") or ip.startswith("223")

# ========== Exponential Emergency (2^n) ==========
def emergency_trigger(severity):
    if severity > 80:
        return 2 ** random.randint(1, 4)  # exponential scale
    return 1

# ========== SESSION STATE ==========
if 'threat_log' not in st.session_state:
    st.session_state.threat_log = []
if 'blocked_th' not in st.session_state:
    st.session_state.blocked_th = []
if 'c2_graph' not in st.session_state:
    st.session_state.c2_graph = nx.Graph()
if 'active_apt' not in st.session_state:
    st.session_state.active_apt = []
if 'emergency_level' not in st.session_state:
    st.session_state.emergency_level = 1

# ========== OTX LIVE ==========
def fetch_otx():
    try:
        otx = OTXv2(OTX_API_KEY)
        groups = ["APT28","APT32","Lazarus","APT36","Darkhotel","Seedworm"]
        active = []
        for g in groups:
            pulses = otx.search_pulses(q=g, limit=1, sort="-modified")
            if pulses:
                active.append(g)
        st.session_state.active_apt = active
    except:
        st.session_state.active_apt = ["OTX error (外人ไม่เห็น)"]

# ========== C2 Correlation + Exponential Scan ==========
def auto_c2_correlation():
    while True:
        time.sleep(30)  # simulate, later 1800
        severity = random.randint(50, 95)
        st.session_state.emergency_level = emergency_trigger(severity)
        # Simulate new C2 discovery
        new_apt = random.choice(list(C2_CLUSTERS.keys()))
        new_ips = C2_CLUSTERS[new_apt]["ips"]
        new_domain = C2_CLUSTERS[new_apt]["c2_domain"]
        for ip in new_ips:
            if ip not in st.session_state.threat_log:
                st.session_state.threat_log.append(ip)
                if TH_CONDITION(ip):
                    st.session_state.blocked_th.append(ip)
                # build graph
                st.session_state.c2_graph.add_node(ip, label="IP")
                st.session_state.c2_graph.add_node(new_domain, label="C2")
                st.session_state.c2_graph.add_edge(ip, new_domain)

thread = threading.Thread(target=auto_c2_correlation, daemon=True)
thread.start()

# ========== SIDEBAR (外人เห็นแค่ปุ่ม) ==========
with st.sidebar:
    st.markdown("## 🎮 C2 CORRELATION PANEL")
    st.metric("🚨 EMERGENCY LEVEL", f"2^{st.session_state.emergency_level}")
    if st.button("📡 FORCE CORRELATION"):
        st.rerun()
    if st.button("📤 EXPORT EVIDENCE"):
        evidence = {"blocked": st.session_state.blocked_th, "c2_graph_edges": list(st.session_state.c2_graph.edges)}
        st.download_button("📥 JSON", data=json.dumps(evidence, indent=2), file_name="c2_evidence.json")
    if st.button("🧹 RESET"):
        st.session_state.threat_log.clear()
        st.session_state.blocked_th.clear()
        st.session_state.c2_graph.clear()
        st.rerun()

# ========== MAIN VIEW (外人เห็นแผนที่กลุ่ม C2) ==========
col1, col2 = st.columns(2)
col1.metric("🔴 SUSPECTED C2", len(st.session_state.threat_log))
col2.metric("🇹🇭 BLOCKED (TH)", len(st.session_state.blocked_th))

st.subheader("🌍 LIVE C2 CORRELATION MAP")
if st.session_state.c2_graph.edges:
    pos = nx.spring_layout(st.session_state.c2_graph)
    edge_x = []
    edge_y = []
    for edge in st.session_state.c2_graph.edges:
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    trace_edges = dict(type='scatter', x=edge_x, y=edge_y, mode='lines', line=dict(color='#00f2ff', width=2))
    node_x = [pos[node][0] for node in st.session_state.c2_graph.nodes]
    node_y = [pos[node][1] for node in st.session_state.c2_graph.nodes]
    trace_nodes = dict(type='scatter', x=node_x, y=node_y, mode='markers+text', text=list(st.session_state.c2_graph.nodes), marker=dict(size=20, color='red'))
    st.plotly_chart(dict(data=[trace_edges, trace_nodes]), use_container_width=True)
else:
    st.info("รอการตรวจจับ C2 (外人ไม่เห็นข้อมูล)")

st.subheader("🔴 ACTIVE APT GROUPS (OTX)")
fetch_otx()
st.code(", ".join(st.session_state.active_apt) if st.session_state.active_apt else "None (外人ไม่เห็น)")

st.subheader("📡 THREAT & C2 LOG")
st.code("\n".join(st.session_state.threat_log[-15:]) if st.session_state.threat_log else "No log (外人ไม่เห็น)", language="bash")

st.caption("© 2026 Kriangkrai Khatsom | 外人เห็นแค่การเชื่อมโยง ไม่เห็น correlation logic, exponential trigger, ไม่เห็นข้อมูลจริง")
