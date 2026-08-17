import streamlit as st
import requests
import pandas as pd
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="Multi-Sport AI Predictor", page_icon="🏆", layout="centered")

st.markdown("<h2 style='text-align: center; color: #38BDF8;'>🏆 Multi-Sport AI Predictor Pro</h2>", unsafe_allow_html=True)

# --- SIDEBAR SPORT SELECTOR ---
st.sidebar.header("⚙️ App Controls")
selected_sport = st.sidebar.radio("🎯 ක්‍රීඩාව තෝරන්න (Select Sport):", ["⚽ Football", "🏏 Cricket"])

# ==========================================
# ⚽ FOOTBALL PREDICTION SECTION
# ==========================================
if selected_sport == "⚽ Football":
    st.subheader("⚽ Football Live & Analytics Predictor")
    
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
    
    # Football Elo + Poisson Engine
    elo_h = 1800 + (sum(ord(c) for c in home) % 150) + 100
    elo_a = 1750 + (sum(ord(c) for c in away) % 150)
    
    prob_h = round((1 / (1 + 10 ** ((elo_a - elo_h) / 400))) * 100, 1)
    prob_a = round(100 - prob_h, 1)
    
    xg_h = max(0.5, round(prob_h * 2.8 / 100, 2))
    xg_a = max(0.3, round(prob_a * 2.8 / 100, 2))
    
    score_h = int(round((prob_h / 100) * 3))
    score_a = int(round((prob_a / 100) * 3))
    
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.metric(f"🚩 {home}", f"{prob_h}%", delta=f"Expected Goals (xG): {xg_h}")
        st.progress(prob_h / 100)
    with col2:
        st.metric(f"🚩 {away}", f"{prob_a}%", delta=f"Expected Goals (xG): {xg_a}")
        st.progress(prob_a / 100)
        
    st.success(f"🎯 **AI Expected Final Score:** {score_h} - {score_a}")
    
    df = pd.DataFrame({
        "Metric": ["Calculated Elo Rating", "Expected Goals (xG)", "Win Probability"],
        home: [elo_h, xg_h, f"{prob_h}%"],
        away: [elo_a, xg_a, f"{prob_a}%"]
    })
    st.dataframe(df, use_container_width=True)

# ==========================================
# 🏏 CRICKET PREDICTION SECTION
# ==========================================
elif selected_sport == "🏏 Cricket":
    st.subheader("🏏 Cricket Live & Analytics Predictor")
    
    cricket_matches = [
        {"team_a": "Sri Lanka", "team_b": "India", "type": "T20 International"},
        {"team_a": "Australia", "team_b": "England", "type": "The Ashes ODI"},
        {"team_a": "Chennai Super Kings", "team_b": "Mumbai Indians", "type": "IPL T20"},
        {"team_a": "Pakistan", "team_b": "South Africa", "type": "World Cup T20"}
    ]
    
    c_list = [f"🏏 {m['team_a']} vs {m['team_b']}" for m in cricket_matches]
    c_idx = st.selectbox("🎯 Target Cricket Match එක තෝරන්න:", range(len(c_list)), format_func=lambda x: c_list[x])
    
    c_match = cricket_matches[c_idx]
    team_a, team_b = c_match['team_a'], c_match['team_b']
    
    # Sidebar Controls for Cricket
    st.sidebar.markdown("---")
    st.sidebar.subheader("🏏 Match Controls")
    toss = st.sidebar.radio("Toss දිනූ කණ්ඩායම:", [team_a, team_b])
    batting = st.sidebar.radio("පළමුව Bat කරන්නේ:", [team_a, team_b])
    pitch = st.sidebar.selectbox("Pitch ස්වභාවය:", ["Balanced", "Batting Friendly", "Bowling/Spin Friendly"])
    
    rating_a = 1500 + (sum(ord(c) for c in team_a) % 200) + (30 if toss == team_a else -30)
    rating_b = 1500 + (sum(ord(c) for c in team_b) % 200)
    
    win_a = round(1 / (1 + 10 ** ((rating_b - rating_a) / 400)) * 100, 1)
    win_b = round(100 - win_a, 1)
    
    runs_a = int(165 + (win_a - 50) * 0.7)
    runs_b = int(165 + (win_b - 50) * 0.7)
    
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.metric(f"🥇 {team_a}", f"{win_a}%", delta=f"Projected Score: {runs_a} Runs")
        st.progress(win_a / 100)
    with col2:
        st.metric(f"🥈 {team_b}", f"{win_b}%", delta=f"Projected Score: {runs_b} Runs")
        st.progress(win_b / 100)
        
    st.success(f"🏆 Win Advantage: **{team_a if win_a > win_b else team_b}**")
    
    df = pd.DataFrame({
        "Metric": ["Team Rating Factor", "Pitch/Toss Effect", "Projected 1st Innings Runs"],
        team_a: [rating_a, "Positive" if toss == team_a else "Neutral", f"{runs_a} Runs"],
        team_b: [rating_b, "Positive" if toss == team_b else "Neutral", f"{runs_b} Runs"]
    })
    st.dataframe(df, use_container_width=True)
