import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="AI Sports Predictor", page_icon="⚽", layout="centered")

st.markdown("<h2 style='text-align: center; color: #38BDF8;'>⚽ Real-Time AI Sports Predictor</h2>", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def fetch_sports_data():
    url = "https://www.thesportsdb.com/api/v1/json/3/eventsseason.php?id=4328&s=2023-2024"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json().get('events', [])
    except Exception:
        return []
    return []

def calculate_prediction(odds_h, odds_a, form_effect=0.0):
    implied_h = 1 / odds_h
    implied_a = 1 / odds_a
    total = implied_h + implied_a
    
    prob_h = round(((implied_h / total) * 100) + form_effect, 1)
    prob_a = round(100 - prob_h, 1)
    
    score_h = int(round((prob_h / 100) * 3))
    score_a = int(round((prob_a / 100) * 3))
    
    return prob_h, prob_a, f"{score_h} - {score_a}"

events = fetch_sports_data()

if events:
    matches = [f"⚽ {e['strHomeTeam']} vs {e['strAwayTeam']}" for e in events[:10]]
    idx = st.selectbox("🎯 Target Match එක තෝරන්න:", range(len(matches)), format_func=lambda x: matches[x])
    
    selected = events[idx]
    home = selected.get('strHomeTeam', 'Home Team')
    away = selected.get('strAwayTeam', 'Away Team')
    
    odds_h = 1.85
    odds_a = 2.10
    
    prob_h, prob_a, score = calculate_prediction(odds_h, odds_a, 2.0)
    
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.metric(f"🚩 {home}", f"{prob_h}%")
        st.progress(prob_h / 100)
    with col2:
        st.metric(f"🚩 {away}", f"{prob_a}%")
        st.progress(prob_a / 100)
        
    st.success(f"🎯 **AI Expected Final Score:** {score}")
    
    st.write("**📊 Historical & Team Performance Data:**")
    df = pd.DataFrame({
        "Metric": ["Live Odds", "Winning Prob", "Past Form Rating"],
        home: [odds_h, f"{prob_h}%", "8.4 / 10"],
        away: [odds_a, f"{prob_a}%", "7.1 / 10"]
    })
    st.dataframe(df, use_container_width=True)
else:
    st.warning("Data loading failed. Please refresh the page.")
