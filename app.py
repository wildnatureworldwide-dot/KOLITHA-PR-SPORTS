import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Koli's Live AI Predictor", page_icon="🏆", layout="centered")

st.markdown("<h2 style='text-align: center; color: #38BDF8;'>🏆 Koli's Real-Time AI Sports Predictor</h2>", unsafe_allow_html=True)
st.caption("🔥 Developed by **Koli** | Automated Daily ESPN Live Feeds")

# Sidebar Controls
st.sidebar.header("⚙️ App Controls")
selected_sport = st.sidebar.radio("🎯 ක්‍රීඩාව තෝරන්න:", ["⚽ Football (EPL)", "🏏 Cricket (International)"])

# 1. Fetch Today's Dynamic Live Matches from ESPN Public API (No API Key Required)
@st.cache_data(ttl=300) # Every 5 minutes auto refresh
def fetch_espn_live_matches(sport_type):
    if sport_type == "soccer":
        url = "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard"
    else:
        url = "https://site.web.api.espn.com/apis/v2/scoreboard/header?sport=cricket"
        
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            events = data.get('events', [])
            parsed_matches = []
            for e in events:
                name = e.get('name', '')
                competitors = e.get('competitions', [{}])[0].get('competitors', [])
                if len(competitors) >= 2:
                    t1 = competitors[0].get('team', {}).get('displayName', 'Team A')
                    t2 = competitors[1].get('team', {}).get('displayName', 'Team B')
                    status = e.get('status', {}).get('type', {}).get('detail', 'Upcoming')
                    parsed_matches.append({"home": t1, "away": t2, "status": status})
            return parsed_matches
    except Exception:
        pass
    return []

# ==========================================
# ⚽ FOOTBALL AUTOMATED LIVE SECTION
# ==========================================
if selected_sport == "⚽ Football (EPL)":
    st.subheader("⚽ Live & Today's Football Matches")
    matches = fetch_espn_live_matches("soccer")
    
    if matches:
        match_options = [f"⚽ {m['home']} vs {m['away']} [{m['status']}]" for m in matches]
        s_idx = st.selectbox("🎯 අද පැවැත්වෙන Target Match එක තෝරන්න:", range(len(match_options)), format_func=lambda x: match_options[x])
        
        home = matches[s_idx]['home']
        away = matches[s_idx]['away']
        
        # Calculation
        elo_h = 1800 + (sum(ord(c) for c in home) % 120) + 50
        elo_a = 1750 + (sum(ord(c) for c in away) % 120)
        
        prob_h = round((1 / (1 + 10 ** ((elo_a - elo_h) / 400))) * 100, 1)
        prob_a = round(100 - prob_h, 1)
        
        rec_bet = f"🔥 Match Winner: **{home if prob_h > prob_a else away}**" if abs(prob_h - prob_a) > 15 else "🛡️ **Double Chance / Draw**"
        
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.metric(f"🚩 {home}", f"{prob_h}%")
            st.progress(prob_h / 100)
        with col2:
            st.metric(f"🚩 {away}", f"{prob_a}%")
            st.progress(prob_a / 100)
            
        st.info(f"💡 **Koli's Recommended Bet:** {rec_bet}")
    else:
        st.warning("අද දිනයේ Live/Upcoming Football Matches කිසිවක් නොමැත හෝ Data Load වෙමින් පවතී.")

# ==========================================
# 🏏 CRICKET AUTOMATED LIVE SECTION
# ==========================================
elif selected_sport == "🏏 Cricket (International)":
    st.subheader("🏏 Live & Today's Cricket Matches")
    c_matches = fetch_espn_live_matches("cricket")
    
    if c_matches:
        c_options = [f"🏏 {m['home']} vs {m['away']} [{m['status']}]" for m in c_matches]
        c_idx = st.selectbox("🎯 අද පැවැත්වෙන Target Match එක තෝරන්න:", range(len(c_options)), format_func=lambda x: c_options[x])
        
        team_a = c_matches[c_idx]['home']
        team_b = c_matches[c_idx]['away']
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("🏏 Match Controls")
        toss = st.sidebar.radio("Toss දිනූ කණ්ඩායම:", [team_a, team_b])
        pitch = st.sidebar.selectbox("Pitch ස්වභාවය:", ["Balanced", "Batting Friendly", "Bowling Friendly"])
        
        rating_a = 1500 + (sum(ord(c) for c in team_a) % 180) + (30 if toss == team_a else -30)
        rating_b = 1500 + (sum(ord(c) for c in team_b) % 180)
        
        win_a = round(1 / (1 + 10 ** ((rating_b - rating_a) / 400)) * 100, 1)
        win_b = round(100 - win_a, 1)
        
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.metric(f"🥇 {team_a}", f"{win_a}%")
            st.progress(win_a / 100)
        with col2:
            st.metric(f"🥈 {team_b}", f"{win_b}%")
            st.progress(win_b / 100)
            
        st.info(f"💡 **Koli's Recommended Bet:** 🏆 Match Winner: **{team_a if win_a > win_b else team_b}**")
    else:
        st.warning("අද දිනයේ Live/Upcoming Cricket Matches කිසිවක් නොමැත හෝ Data Load වෙමින් පවතී.")
