# ========== OTX LIVE APT GROUPS ==========
st.subheader("🔴 OTX LIVE APT GROUPS (AlienVault)")

# ถ้าไม่มี OTX Key ให้ข้าม
try:
    from OTXv2 import OTXv2
    otx_key = st.secrets["otx_api_key"]
    otx = OTXv2(otx_key)
    apt_groups = ["APT28", "APT32", "Lazarus", "APT36", "Darkhotel", "Seedworm"]
    active_groups = []
    for grp in apt_groups:
        pulses = otx.search_pulses(q=grp, limit=1, sort="-modified")
        if pulses:
            active_groups.append(grp)
    st.write(", ".join(active_groups))
except Exception as e:
    st.warning("OTX not available (外人ไม่เห็น API key)")
