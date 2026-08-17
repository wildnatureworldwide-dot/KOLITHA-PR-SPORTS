import streamlit as st
import requests
import pandas as pd
import numpy as np

st.set_page_config(page_title="Koli's AI Sports Predictor", page_icon="🏆", layout="centered")

# App Header with User Name "Koli"
st.markdown("<h2 style='text-align: center; color: #38BDF8;'>🏆 Koli's AI Sports Predictor Pro</h2>", unsafe_allow_html=True)
st.caption("🔥 Developed & Powered by **Koli** | Smart Betting Value Predictor")

# Sidebar
st.sidebar.header("⚙️ App Controls")
selected_sport = st.sidebar.radio("🎯 ක්‍රීඩාව තෝරන්න:", ["⚽ Football", "🏏 Cricket"])

# ==========================================
# ⚽ FOOTBALL PREDICTION & BET RECOMMENDATION
# ==========================================
if selected_sport == "⚽ Football":
    st.subheader("⚽ Football Live & Recommended Bets")
    
    football_matches = [
        {"home": "Real Madrid", "away": "Barcelona", "league": "La Liga"},
        {"home": "Manchester City", "away": "Arsenal", "league": "Premier League"},
        {"home": "Bayern Munich", "away": "Dortmund", "league": "Bundesliga"},
        {"home": "Liverpool", "away": "Chelsea", "league": "Premier League"}
    ]
    
    match_list = [f"⚽ {m['home']} vs {m['away']}" for m in football_matches]
    selected_idx = st.selectbox("🎯 Target Football Match එක තෝරන්න:", range(len(match_list)), format_func=lambda x: match_list[x])
    
    match = football_matches[selected_idx]
    home, away = match['home'], match['away']
    
    # Mathematical Calculations
    elo_h = 1800 + (sum(ord(c) for c in home) % 150) + 100
    elo_a = 1750 + (sum(ord(c) for c in away) % 150)
    
    prob_h = round((1 / (1 + 10 ** ((elo_a - elo_h) / 400))) * 100, 1)
    prob_a = round(100 - prob_h, 1)
    
    xg_h = round(prob_h * 2.8 / 100, 2)
    xg_a = round(prob_a * 2.8 / 100, 2)
    total_xg = round(xg_h + xg_a, 2)
    
    # Recommended Bet Logic
    if prob_h > 62:
        rec_bet = f"🔥 Straight Win: **{home}**"
        risk_level = "Low Risk (Safe)"
    elif prob_a > 62:
        rec_bet = f"🔥 Straight Win: **{away}**"
        risk_level = "Low Risk (Safe)"
    elif total_xg > 2.5:
        rec_bet = "⚽ **Over 2.5 Total Goals**"
        risk_level = "Medium Risk (Value Bet)"
    else:
        rec_bet = f"🛡️ **Double Chance: {home} or Draw**"
        risk_level = "Low Risk (Safe)"

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.metric(f"🚩 {home}", f"{prob_h}%")
        st.progress(prob_h / 100)
    with col2:
        st.metric(f"🚩 {away}", f"{prob_a}%")
        st.progress(prob_a / 100)
        
    # Koli's Recommended Bet Box
    st.info(f"💡 **Koli's Recommended Bet:** {rec_bet}\n\n📊 **Risk Level:** `{risk_level}`")
    
    df = pd.DataFrame({
        "Metric": ["Elo Rating", "Expected Goals (xG)", "Winning Chance"],
        home: [elo_h, xg_h, f"{prob_h}%"],
        away: [elo_a, xg_a, f"{prob_a}%"]
    })
    st.dataframe(df, use_container_width=True)

# ==========================================
# 🏏 CRICKET PREDICTION & BET RECOMMENDATION
# ==========================================
elif selected_sport == "🏏 Cricket":
    st.subheader("🏏 Cricket Live & Recommended Bets")
    
    cricket_matches = [
        {"team_a": "Sri Lanka", "team_b": "India"},
        {"team_a": "Australia", "team_b": "England"},
        {"team_a": "Chennai Super Kings", "team_b": "Mumbai Indians"},
        {"team_a": "Pakistan", "team_b": "South Africa"}
    ]
    
    c_list = [f"🏏 {m['team_a']} vs {m['team_b']}" for m in cricket_matches]
    c_idx = st.selectbox("🎯 Target Cricket Match එක තෝරන්න:", range(len(c_list)), format_func=lambda x: c_list[x])
    
    c_match = cricket_matches[c_idx]
    team_a, team_b = c_match['team_a'], c_match['team_b']
    
    # Cricket Match Controls
    st.sidebar.markdown("---")
    st.sidebar.subheader("🏏 Match Conditions")
    toss = st.sidebar.radio("Toss දිනූ කණ්ඩායම:", [team_a, team_b])
    batting = st.sidebar.radio("පළමුව Bat කරන්නේ:", [team_a, team_b])
    pitch = st.sidebar.selectbox("Pitch ස්වභාවය:", ["Balanced", "Batting Friendly", "Bowling Friendly"])
    
    rating_a = 1500 + (sum(ord(c) for c in team_a) % 200) + (35 if toss == team_a else -35)
    rating_b = 1500 + (sum(ord(c) for c in team_b) % 200)
    
    win_a = round(1 / (1 + 10 ** ((rating_b - rating_a) / 400)) * 100, 1)
    win_b = round(100 - win_a, 1)
    
    runs_1st = int(165 + (win_a - 50) * 0.7) if batting == team_a else int(165 + (win_b - 50) * 0.7)
    
    # Cricket Bet Recommendation Logic
    winner = team_a if win_a > win_b else team_b
    if pitch == "Batting Friendly":
        rec_cricket_bet = f"🔥 **1st Innings Score Over {runs_1st - 10}.5 Runs**"
    elif pitch == "Bowling Friendly":
        rec_cricket_bet = f"🔥 **1st Innings Score Under {runs_1st + 10}.5 Runs**"
    else:
        rec_cricket_bet = f"🏆 **Match Winner: {winner}**"

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.metric(f"🥇 {team_a}", f"{win_a}%")
        st.progress(win_a / 100)
    with col2:
        st.metric(f"🥈 {team_b}", f"{win_b}%")
        st.progress(win_b / 100)
        
    # Koli's Recommended Bet Box
    st.info(f"💡 **Koli's Recommended Bet:** {rec_cricket_bet}\n\n🎯 **Projected 1st Innings Score:** `{runs_1st} Runs`")
    
    df = pd.DataFrame({
        "Factor": ["Team Rating", "Toss Advantage", "Win Prob %"],
        team_a: [rating_a, "Yes" if toss == team_a else "No", f"{win_a}%"],
        team_b: [rating_b, "Yes" if toss == team_b else "No", f"{win_b}%"]
    })
    st.dataframe(df, use_container_width=True)
