import streamlit as st
import requests

st.set_page_config(page_title="Auto Sports AI Predictor", layout="centered")

st.title("⚽ Automated Live Sports Predictor AI")
st.write("Live Data, Player History & Team Changes මත පදනම්ව automatic සෑදූ Predictions:")

# 1. Automatic Live Sports Data Fetching (Free Live API)
@st.cache_data(ttl=60)  # තත්පර 60න් 60ට Automatic Refresh වේ
def fetch_live_data():
    # Example API endpoint for live match data
    url = "https://www.thesportsdb.com/api/v1/json/3/eventslast.php?id=133602"
    try:
        res = requests.get(url).json()
        return res.get('results', [])
    except:
        return []

# 2. Automated Prediction Engine (Odds + Player History + Live Changes)
def calculate_prediction(team_a_rating, team_b_rating, live_changes_a=0, live_changes_b=0):
    # Adjust rating based on live lineup/player status changes
    adj_a = team_a_rating + live_changes_a
    adj_b = team_b_rating + live_changes_b
    
    total = adj_a + adj_b
    win_pct_a = round((adj_a / total) * 100, 1)
    win_pct_b = round((adj_b / total) * 100, 1)
    
    # Score Estimation Logic based on weighted ratings
    est_score_a = int((win_pct_a / 100) * 3)
    est_score_b = int((win_pct_b / 100) * 3)
    
    return win_pct_a, win_pct_b, f"{est_score_a} - {est_score_b}"

# --- UI display ---
st.subheader("🔥 Top Match Prediction")

# Simulated Live Data Inputs (In production, fetched automatically from API)
team_a = "Real Madrid"
team_b = "Barcelona"
team_a_past_form = 88.5  # Historical performance rating
team_b_past_form = 79.0

# Live Team Lineup/Player Change adjustment (-5 to +5 based on missing/new key players)
live_lineup_effect_a = 2.0   # Key player in good form added
live_lineup_effect_b = -3.0  # Key player injured/red carded

win_a, win_b, est_score = calculate_prediction(
    team_a_past_form, team_b_past_form, live_lineup_effect_a, live_lineup_effect_b
)

col1, col2 = st.columns(2)
with col1:
    st.metric(label=f"🚩 {team_a} Win Chance", value=f"{win_a}%")
with col2:
    st.metric(label=f"🚩 {team_b} Win Chance", value=f"{win_b}%")

st.info(f"🎯 **Estimated Score:** {est_score}")

if win_a > win_b:
    st.success(f"🏆 **Highest Winning Probability:** {team_a}")
else:
    st.success(f"🏆 **Highest Winning Probability:** {team_b}")
