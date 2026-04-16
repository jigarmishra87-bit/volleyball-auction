import streamlit as st
import pandas as pd
import os
import base64
import time
import threading
import plotly.express as px
import urllib.parse
from streamlit_autorefresh import st_autorefresh

# 🔗 BACKEND CONNECTION
import db_manager as dbm

st.set_page_config(page_title="Mega Volleyball Auction 2026", layout="wide", page_icon="🏐")

@st.cache_resource
def get_lock(): return threading.Lock()
db_lock = get_lock()

DISCORD_LINK = "https://discord.gg/ePnD2Qqkj"
WHATSAPP_GROUP_LINK = "https://chat.whatsapp.com/KTPQNGAMGh065WGJ8LmsYn"
APP_URL = "https://volleyball-auction.streamlit.app" 

if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'user_role': None, 'team_name': None})

# 📥 DATA LOAD
db = dbm.load_db()
USER_DATA = db["users"]
players = db["players"]
teams = [v["team"] for k, v in USER_DATA.items() if k != "Masterji"]
sold_data = db.get("sold_data", [])

def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return None

b64 = get_base64("volleyball.webp")
if b64:
    st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(rgba(10, 15, 20, 0.9), rgba(10, 15, 20, 0.9)), url(data:image/webp;base64,{b64}); background-size: cover; background-position: center; background-attachment: fixed; }}
    .big-title {{ text-align: center; font-size: 50px !important; font-weight: 900; color: #FFD700; text-transform: uppercase; text-shadow: 3px 3px 6px #000; letter-spacing: 2px; }}
    .player-card {{ background: rgba(25, 25, 25, 0.95); padding: 45px; border-radius: 30px; border: 3px solid #FFD700; backdrop-filter: blur(10px); box-shadow: 0 0 50px rgba(255, 215, 0, 0.2); text-align: center; margin: 10px auto; max-width: 600px; }}
    .photo-frame {{ width: 240px; height: 240px; border-radius: 50%; border: 6px solid #FFD700; box-shadow: 0 0 30px rgba(255, 215, 0, 0.5); object-fit: cover; background: #111; margin: 0 auto 20px auto; display: block; }}
    .category-badge {{ background-color: #FF4500; color: white; padding: 10px 25px; border-radius: 15px; font-weight: bold; font-size: 22px; text-transform: uppercase; display: inline-block; }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN UI ---
if not st.session_state['logged_in']:
    st.markdown("<h1 class='big-title'>🏐 AUCTION ARENA LOGIN</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        lc1, lc2 = st.columns(2)
        lc1.link_button("🎙️ DISCORD", DISCORD_LINK, use_container_width=True)
        lc2.link_button("💬 WHATSAPP", WHATSAPP_GROUP_LINK, use_container_width=True)
        with st.form("login_form"):
            uid = st.text_input("User ID")
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("ENTER ARENA", type="primary"):
                if uid in USER_DATA and USER_DATA[uid]["password"] == pwd:
                    st.session_state.update({'logged_in':True, 'user_role':uid, 'team_name':USER_DATA[uid]["team"]})
                    st.rerun()
                else: st.error("❌ Invalid Credentials")
        st.markdown("---")
        if st.button("👁️ WATCH LIVE AS GUEST", use_container_width=True):
            st.session_state.update({'logged_in':True, 'user_role':'viewer', 'team_name':'👤 LIVE AUDIENCE'})
            st.rerun()
    st.stop()

# --- SIDEBAR & REFRESH CONTROL ---
spent = {t: sum(x["Final Points"] for x in sold_data if x["Sold To"] == t) for t in teams}
purses = {t: dbm.TOTAL_PURSE - spent.get(t, 0) for t in teams}

with st.sidebar:
    st.markdown(f"### 🚩 {st.session_state['team_name']}")
    if st.button("LOGOUT"): st.session_state['logged_in'] = False; st.rerun()
    st.write("---")
    
    # MASTER SWITCH (Form bharte waqt band kar dein)
    is_auto_refresh = st.toggle("🟢 Live Auto-Refresh", value=True)
    
    st.write("---")
    st.link_button("🎤 Join War Room", DISCORD_LINK, use_container_width=True)
    st.link_button("💬 Join Group", WHATSAPP_GROUP_LINK, use_container_width=True)
    st.write("---")
    if teams and sum(purses.values()) > 0:
        fig = px.pie(values=list(purses.values()), names=list(purses.keys()), hole=0.6, color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    for t in teams: st.caption(f"{t}: {purses[t]} pts")

# ⚡ AUTO-REFRESH (Only if Toggled ON)
if st.session_state['logged_in'] and is_auto_refresh:
    st_autorefresh(interval=1500, limit=10000, key="data_refresh")

sold_names = [x["Player"].replace(" (RTM)", "").replace(" (Retained)", "") for x in sold_data]
while db["player_index"] < len(players) and players[db["player_index"]]["Name"] in sold_names:
    db["player_index"] += 1

# --- MAIN ARENA ---
st.markdown(f"<p class='big-title'>🏆 AUCTION DASHBOARD 🏆</p>", unsafe_allow_html=True)

if db["player_index"] >= len(players):
    st.success("🎉 AUCTION COMPLETED!")
else:
    current_player = players[db["player_index"]]
    actual_base = current_player["Base_Points"] // 2 if db.get("round_2") else current_player["Base_Points"]
    
    if db["current_team"] != "None":
        elapsed = time.time() - db.get("last_bid_time", time.time())
        time_left = max(0, 20 - int(elapsed))
        st.markdown(f"<h2 style='text-align: center; color: {'#FF4500' if time_left <= 5 else '#00FA9A'};'>⏳ AUTO-SELL IN: {time_left}s</h2>", unsafe_allow_html=True)
        if time_left == 0:
            with db_lock:
                fdb = dbm.load_db()
                fdb["sold_data"].append({"Player": current_player["Name"], "Sold To": fdb["current_team"], "Final Points": fdb["current_bid"]})
                fdb.update({"player_index":fdb["player_index"]+1, "current_bid":0, "current_team":"None", "passed_teams":[], "last_bid_time":time.time()})
                dbm.save_db(fdb)
            st.rerun()

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        p_img_b64 = get_base64(current_player.get("Photo", "default.jpg"))
        p_html = f'<img src="data:image/jpeg;base64,{p_img_b64}" class="photo-frame">' if p_img_b64 else '<div class="photo-frame" style="display:flex; align-items:center; justify-content:center; font-size:100px;">🏐</div>'
        st.markdown(f'<div class="player-card">{p_html}<span class="category-badge">{current_player["Role"]}</span><h1 style="color:#FFD700; margin-top:20px; font-size:60px;">{current_player["Name"]}</h1><h2 style="color:#00FA9A;">BASE: {actual_base} PTS</h2></div>', unsafe_allow_html=True)

    # 3 COLUMNS ONLY (Viewers Removed)
    st.write("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("HIGHEST BID", f"{db['current_bid']}")
    m2.metric("CURRENT BIDDER", db["current_team"])
    m3.metric("YOUR BUDGET", purses.get(st.session_state['team_name'], "0"))

    if st.session_state['user_role'] not in ["Masterji", "viewer"]:
        me = st.session_state['team_name']
        nxt = db["current_bid"] + 100 if db["current_team"] != "None" else actual_base
        bc1, bc2, bc3 = st.columns(3)
        with bc1:
            if st.button(f"🚀 RAISE BID {nxt}", disabled=(purses.get(me, 0) < nxt or me in db.get("passed_teams", [])), use_container_width=True, type="primary"):
                with db_lock:
                    fdb = dbm.load_db(); fdb.update({"current_team":me, "current_bid":nxt, "last_bid_time":time.time(), "passed_teams":[]})
                    dbm.save_db(fdb)
                st.rerun()
        with bc2:
            if st.button("❌ PASS", disabled=(me in db.get("passed_teams", []) or me == db["current_team"]), use_container_width=True):
                with db_lock:
                    fdb = dbm.load_db(); fdb.setdefault("passed_teams", []).append(me); dbm.save_db(fdb)
                st.rerun()
        with bc3:
            can_rtm = db.get("rtm_cards", {}).get(me) and db["current_team"] not in ["None", me]
            if st.button("🃏 USE RTM", disabled=not can_rtm, use_container_width=True):
                with db_lock:
                    fdb = dbm.load_db(); fdb["sold_data"].append({"Player": current_player["Name"] + " (RTM)", "Sold To": me, "Final Points": fdb["current_bid"]})
                    fdb["rtm_cards"][me] = False; fdb.update({"player_index":fdb["player_index"]+1, "current_bid":0, "current_team":"None"})
                    dbm.save_db(fdb)
                st.rerun()

# --- COMMAND CENTER ---
if st.session_state['user_role'] == "Masterji":
    with st.expander("🛠️ MASTERJI COMMAND CENTER", expanded=True):
        msg = f"🏐 *Auction Alert!* \nJoin Live: {APP_URL}"
        st.link_button("📢 SEND WHATSAPP NOTIFICATION", f"https://wa.me/?text={urllib.parse.quote(msg)}", use_container_width=True)
        st.write("---")
        
        st.markdown("#### ⚡ Quick Actions")
        ac1, ac2, ac3 = st.columns(3)
        with ac1:
            if db["player_index"] < len(players) and st.button("🔨 FORCE SOLD"):
                with db_lock:
                    fdb = dbm.load_db(); fdb["sold_data"].append({"Player": current_player["Name"], "Sold To": fdb["current_team"], "Final Points": fdb["current_bid"]})
                    fdb.update({"player_index":fdb["player_index"]+1, "current_bid":0, "current_team":"None"}); dbm.save_db(fdb)
                st.rerun()
        with ac2:
            if db["player_index"] < len(players) and st.button("❌ FORCE UNSOLD"):
                with db_lock:
                    fdb = dbm.load_db(); fdb["sold_data"].append({"Player": current_player["Name"], "Sold To": "UNSOLD", "Final Points": 0})
                    fdb.update({"player_index":fdb["player_index"]+1, "current_bid":0, "current_team":"None"}); dbm.save_db(fdb)
                st.rerun()
        with ac3:
            if st.button("🔄 EMERGENCY RESET DB", type="primary"):
                with db_lock: dbm.save_db(dbm.get_default_db())
                st.rerun()

        st.write("---")
        avail = [p["Name"] for p in players if p["Name"] not in sold_names]
        st.markdown("#### 🎯 Call Player")
        call = st.selectbox("Select Player", avail) if avail else None
        if st.button("📢 BRING TO STAGE", disabled=not avail):
            if call:
                idx = next(i for i, p in enumerate(players) if p["Name"] == call)
                with db_lock:
                    fdb = dbm.load_db(); fdb.update({"player_index":idx, "current_bid":0, "current_team":"None"}); dbm.save_db(fdb)
                st.rerun()

        st.write("---")
        st.markdown("#### ⚙️ Manage Teams")
        tm1, tm2 = st.columns(2)
        with tm1:
            with st.form("add_team"):
                st.write("**➕ Add New Team**")
                ni = st.text_input("New ID")
                np = st.text_input("Password", type="password")
                nn = st.text_input("Team Name")
                if st.form_submit_button("Add Team"):
                    with db_lock:
                        fdb = dbm.load_db(); fdb["users"][ni] = {"password":np, "team":nn}; fdb["rtm_cards"][nn]=True
                        dbm.save_db(fdb)
                    st.rerun()
        with tm2:
            with st.form("rem_team"):
                st.write("**🗑️ Remove Team**")
                rem_options = [k for k in db["users"] if k != "Masterji"]
                ri = st.selectbox("Remove Team", rem_options) if rem_options else None
                if st.form_submit_button("Remove", disabled=not rem_options):
                    if ri:
                        with db_lock:
                            fdb = dbm.load_db(); del fdb["users"][ri]; dbm.save_db(fdb)
                        st.rerun()

        st.write("---")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("#### 🤝 Retain Player")
            ret_player = st.selectbox("Select Player", avail, key="ret_p") if avail else None
            ret_team = st.selectbox("Retain To", teams) if teams else None
            ret_price = st.number_input("Retain Price", min_value=0, step=100)
            if st.button("🤝 Confirm Retain", use_container_width=True, disabled=not (avail and teams)):
                if ret_player and ret_team:
                    with db_lock:
                        fdb = dbm.load_db()
                        fdb["sold_data"].append({"Player": ret_player + " (Retained)", "Sold To": ret_team, "Final Points": ret_price})
                        fdb.update({"current_bid":0, "current_team":"None"})
                        dbm.save_db(fdb)
                    st.rerun()

        with col_m2:
            st.markdown("#### 🚫 Mark Unavailable")
            un_player = st.selectbox("Select Player to Mark", avail, key="un_p") if avail else None
            if st.button("🚫 Mark as Unavailable", use_container_width=True, disabled=not avail):
                if un_player:
                    with db_lock:
                        fdb = dbm.load_db()
                        fdb["sold_data"].append({"Player": un_player, "Sold To": "UNAVAILABLE", "Final Points": 0})
                        if fdb["player_index"] < len(fdb["players"]) and current_player["Name"] == un_player:
                            fdb.update({"player_index":fdb["player_index"]+1, "current_bid":0, "current_team":"None"})
                        dbm.save_db(fdb)
                    st.rerun()

        st.write("---")
        st.markdown("#### ➕ Add New Player")
        with st.form("add_player_form"):
            np_name = st.text_input("Player Name")
            np_role = st.selectbox("Role", ["OUTSIDE HITTER", "RIGHT SIDE HITTER", "SETTER", "MIDDLE BLOCKER", "LIBERO", "ALL ROUNDER", "SERVICE SPECIALIST"])
            np_base = st.number_input("Base Price", min_value=100, step=100, value=500)
            if st.form_submit_button("➕ Add Player to Draft", type="primary"):
                if np_name:
                    with db_lock:
                        fdb = dbm.load_db()
                        np_photo = np_name.lower().replace(" ", "") + ".jpg"
                        fdb["players"].append({"Name": np_name.upper(), "Photo": np_photo, "Role": np_role, "Base_Points": np_base})
                        dbm.save_db(fdb)
                    st.rerun()

st.write("---")
if teams:
    tabs = st.tabs([f"🛡️ {t}" for t in teams])
    for i, t in enumerate(teams):
        with tabs[i]:
            df = pd.DataFrame([x for x in sold_data if x["Sold To"] == t])
            if not df.empty: st.dataframe(df, use_container_width=True, hide_index=True)
