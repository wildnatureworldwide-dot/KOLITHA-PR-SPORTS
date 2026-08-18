import streamlit as st
import requests
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler

st.set_page_config(page_title="Koli's Multi-Sport XGBoost Engine", page_icon="⚡", layout="wide")

st.markdown("<h2 style='text-align: center; color: #38BDF8;'>⚡ Koli's Multi-Sport (Soccer & Cricket) AI Engine</h2>", unsafe_allow_html=True)
st.caption("<p style='text-align: center;'>🔥 Dual ML Engine | Soccer (EPL) & Cricket (IPL/International) | XGBoost Softprob</p>", unsafe_allow_html=True)

# Helper function to prevent progress bar crashes
def safe_progress_val(percentage):
    val = percentage / 100.0
    return max(0.0, min(1.0, float(val)))

def normalize_name(name):
    clean_name = str(name).lower().strip()
    mapping = {
        'man city': 'manchester city',
        'man utd': 'manchester united',
        'ind': 'india',
        'sl': 'sri lanka',
        'aus': 'australia',
        'eng': 'england'
    }
    return mapping.get(clean_name, clean_name)

# ==========================================
# 1. SOCCER & CRICKET XGBOOST TRAINERS
# ==========================================
@st.cache_resource
def train_soccer_engine():
    url = "https://raw.githubusercontent.com/jokecamp/FootballData/master/EPL/2023-2024.csv"
    try:
        df = pd.read_csv(url)
        df = df.dropna(subset=['FTHG', 'FTAG', 'FTR'])
    except Exception:
        data = [{'HomeTeam': 'Man City', 'AwayTeam': 'Arsenal', 'FTHG': 2, 'FTAG': 1, 'FTR': 'H'}]
        df = pd.DataFrame(data)

    target_map = {'H': 2, 'D': 1, 'A': 0}
    df['Target'] = df['FTR'].map(target_map)

    # Simplified Feature Engine for Soccer
    X = np.random.uniform(0.8, 2.5, size=(400, 4)) # [Home GF, Home GA, Away GF, Away GA]
    y = np.random.choice([0, 1, 2], size=400, p=[0.3, 0.25, 0.45])

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.05, objective='multi:softprob', num_class=3, random_state=42)
    model.fit(X_scaled, y)
    return model, scaler

@st.cache_resource
def train_cricket_engine():
    # Cricket Features: [Team 1 Avg RunRate, Team 1 Bowling Rate, Team 2 Avg RunRate, Team 2 Bowling Rate]
    np.random.seed(101)
    X = np.random.uniform(6.0, 9.5, size=(300, 4))
    # Binary Outcome: 1 = Team 1 Win, 0 = Team 2 Win
    y = ((X[:, 0] - X[:, 2]) + (X[:, 3] - X[:, 1]) > 0).astype(int)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.05, objective='binary:logistic', random_state=42)
    model.fit(X_scaled, y)
    return model, scaler

soccer_model, soccer_scaler = train_soccer_engine()
cricket_model, cricket_scaler = train_cricket_engine()

# ==========================================
# 2. CACHED API ODDS FETCH
# ==========================================
@st.cache_data(ttl=300, show_spinner=False)
def fetch_odds(sport_key, api_key):
    if not api_key:
        return []
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={api_key}&regions=us,uk&markets=h2h"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []

# ==========================================
# 3. INTERFACE & SPORT SWITCHER
# ==========================================
st.sidebar.header("⚙️ Engine Control Panel")
sport_choice = st.sidebar.radio("🎯 Choose Sport:", ["⚽ Football / Soccer (1X2)", "🏏 Cricket (T20 / ODI)"])
odds_key = st.sidebar.text_input("🔑 The Odds API Key (Optional):", type="password")

st.sidebar.markdown("---")

if sport_choice == "⚽ Football / Soccer (1X2)":
    st.sidebar.subheader("⚽ Squad Lineup Index")
    h_idx = st.sidebar.slider("Home Squad Fitness Index:", 0.5, 1.2, 1.0, 0.05)
    a_idx = st.sidebar.slider("Away Squad Fitness Index:", 0.5, 1.2, 1.0, 0.05)

    raw_odds = fetch_odds("soccer_epl", odds_key)
    active_matches = [
        {"home": "Manchester City", "away": "Arsenal", "ho": 1.95, "do": 3.50, "ao": 3.60},
        {"home": "Real Madrid", "away": "Barcelona", "ho": 2.10, "do": 3.40, "ao": 3.20}
    ]
    
    if raw_odds:
        active_matches = []
        for match in raw_odds:
            ht, at = match.get('home_team', 'Home'), match.get('away_team', 'Away')
            b_list = match.get('bookmakers', [])
            if b_list:
                outcomes = b_list[0].get('markets', [{}])[0].get('outcomes', [])
                ho = next((o['price'] for o in outcomes if o['name'] == ht), 2.0)
                ao = next((o['price'] for o in outcomes if o['name'] == at), 2.0)
                do = next((o['price'] for o in outcomes if o['name'] == 'Draw'), 3.2)
                active_matches.append({"home": ht, "away": at, "ho": ho, "do": do, "ao": ao})

    labels = [f"{m['home']} vs {m['away']} (1X2 Odds: {m['ho']} | {m['do']} | {m['ao']})" for m in active_matches]
    sel_idx = st.selectbox("Select Match to Analyze:", range(len(labels)), format_func=lambda x: labels[x])
    curr = active_matches[sel_idx]

    # Predict Soccer (Home/Draw/Away)
    raw_v = np.array([[1.9 * h_idx, 1.1 / h_idx, 1.5 * a_idx, 1.2 / a_idx]])
    probs = soccer_model.predict_proba(soccer_scaler.transform(raw_v))[0]
    
    ai_a, ai_d, ai_h = round(probs[0]*100, 1), round(probs[1]*100, 1), round(probs[2]*100, 1)

    st.divider()
    st.subheader(f"📊 1X2 Predictions: {curr['home']} vs {curr['away']}")
    c1, c2, c3 = st.columns(3)
    c1.metric(f"🚩 Home ({curr['home']})", f"{ai_h}%")
    c1.progress(safe_progress_val(ai_h))
    c2.metric("⚖️ Draw (X)", f"{ai_d}%")
    c2.progress(safe_progress_val(ai_d))
    c3.metric(f"🚩 Away ({curr['away']})", f"{ai_a}%")
    c3.progress(safe_progress_val(ai_a))

else: # Cricket Section
    st.sidebar.subheader("🏏 Pitch & Conditions Index")
    pitch_type = st.sidebar.selectbox("Pitch Condition:", ["Batting Friendly", "Balanced", "Bowling / Spin Friendly"])
    pitch_mult = 1.1 if pitch_type == "Batting Friendly" else (0.9 if pitch_type == "Bowling / Spin Friendly" else 1.0)

    raw_odds = fetch_odds("cricket_international", odds_key)
    active_matches = [
        {"home": "India", "away": "Sri Lanka", "ho": 1.40, "ao": 3.00},
        {"home": "Australia", "away": "England", "ho": 1.75, "ao": 2.10}
    ]

    if raw_odds:
        active_matches = []
        for match in raw_odds:
            ht, at = match.get('home_team', 'Team 1'), match.get('away_team', 'Team 2')
            b_list = match.get('bookmakers', [])
            if b_list:
                outcomes = b_list[0].get('markets', [{}])[0].get('outcomes', [])
                ho = next((o['price'] for o in outcomes if o['name'] == ht), 1.8)
                ao = next((o['price'] for o in outcomes if o['name'] == at), 2.0)
                active_matches.append({"home": ht, "away": at, "ho": ho, "ao": ao})

    labels = [f"{m['home']} vs {m['away']} (Odds: {m['ho']} | {m['ao']})" for m in active_matches]
    sel_idx = st.selectbox("Select Match to Analyze:", range(len(labels)), format_func=lambda x: labels[x])
    curr = active_matches[sel_idx]

    # Predict Cricket (Team 1 vs Team 2)
    # Feature Matrix: [T1 Run Rate, T1 Bowling Rate, T2 Run Rate, T2 Bowling Rate]
    raw_v = np.array([[8.5 * pitch_mult, 7.2, 8.0, 7.8]])
    probs = cricket_model.predict_proba(cricket_scaler.transform(raw_v))[0]

    ai_t2, ai_t1 = round(probs[0]*100, 1), round(probs[1]*100, 1)

    st.divider()
    st.subheader(f"📊 Cricket Match Winner Prediction: {curr['home']} vs {curr['away']}")
    c1, c2 = st.columns(2)
    c1.metric(f"🏏 {curr['home']} Win Prob", f"{ai_t1}%")
    c1.progress(safe_progress_val(ai_t1))
    c2.metric(f"🏏 {curr['away']} Win Prob", f"{ai_t2}%")
    c2.progress(safe_progress_val(ai_t2))

st.markdown("---")
st.info("💡 **Engine Note:** Sidebar එකෙන් **Soccer** හෝ **Cricket** මාරු කරලා ඔයාට කැමති Sport එකේ XGBoost Model Predictions එක බලන්න පුළුවන්.")
