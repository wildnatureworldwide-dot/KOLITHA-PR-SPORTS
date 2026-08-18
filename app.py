import streamlit as st
import requests
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler

st.set_page_config(page_title="Koli's Pro 1X2 XGBoost Engine", page_icon="⚽", layout="wide")

st.markdown("<h2 style='text-align: center; color: #38BDF8;'>⚽ Koli's Enterprise 1X2 Multi-Class XGBoost Engine</h2>", unsafe_allow_html=True)
st.caption("<p style='text-align: center;'>🔥 Zero Data-Leakage | Dynamic Pre-Match Rolling Averages | 1X2 Multi-Class XGBoost</p>", unsafe_allow_html=True)

# Helper function to prevent progress bar crashes
def safe_progress_val(percentage):
    """Converts 0-100 percentage to safe 0.0-1.0 float for st.progress"""
    val = percentage / 100.0
    return max(0.0, min(1.0, float(val)))

# ==========================================
# 1. TEAM NAME NORMALIZATION ENGINE
# ==========================================
def normalize_team_name(name):
    clean_name = str(name).lower().strip()
    mapping = {
        'man city': 'manchester city',
        'man utd': 'manchester united',
        'man united': 'manchester united',
        'spurs': 'tottenham',
        'tottenham hotspur': 'tottenham',
        'wolves': 'wolverhampton wanderers',
        'wolverhampton': 'wolverhampton wanderers',
        'west ham united': 'west ham',
        'newcastle united': 'newcastle'
    }
    return mapping.get(clean_name, clean_name)

# ==========================================
# 2. DATA PIPELINE & PRE-MATCH ROLLING STATS
# ==========================================
@st.cache_resource
def load_and_train_1x2_model():
    url = "https://raw.githubusercontent.com/jokecamp/FootballData/master/EPL/2023-2024.csv"
    try:
        df = pd.read_csv(url)
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        df = df.sort_values('Date').dropna(subset=['FTHG', 'FTAG', 'FTR'])
    except Exception:
        dates = pd.date_range(start='2023-08-01', periods=380, freq='D')
        teams = ['Arsenal', 'Chelsea', 'Liverpool', 'Manchester City', 'Manchester United', 'Real Madrid', 'Barcelona']
        data = []
        for d in dates:
            ht, at = np.random.choice(teams, size=2, replace=False)
            hg, ag = np.random.poisson(1.6), np.random.poisson(1.2)
            ftr = 'H' if hg > ag else ('A' if ag > hg else 'D')
            data.append({'Date': d, 'HomeTeam': ht, 'AwayTeam': at, 'FTHG': hg, 'FTAG': ag, 'FTR': ftr})
        df = pd.DataFrame(data)

    target_map = {'H': 2, 'D': 1, 'A': 0}
    df['Target'] = df['FTR'].map(target_map)

    team_stats = {}
    processed_rows = []

    for idx, row in df.iterrows():
        ht = normalize_team_name(row['HomeTeam'])
        at = normalize_team_name(row['AwayTeam'])
        
        h_roll = team_stats.get(ht, {'gf': 1.5, 'ga': 1.1, 'matches': 1})
        a_roll = team_stats.get(at, {'gf': 1.4, 'ga': 1.2, 'matches': 1})
        
        processed_rows.append({
            'HomeTeam': ht, 'AwayTeam': at,
            'H_Roll_GF': h_roll['gf'], 'H_Roll_GA': h_roll['ga'],
            'A_Roll_GF': a_roll['gf'], 'A_Roll_GA': a_roll['ga'],
            'Target': row['Target']
        })
        
        for t, gf, ga in [(ht, row['FTHG'], row['FTAG']), (at, row['FTAG'], row['FTHG'])]:
            if t not in team_stats:
                team_stats[t] = {'gf': float(gf), 'ga': float(ga), 'matches': 1}
            else:
                m = team_stats[t]['matches']
                team_stats[t]['gf'] = (team_stats[t]['gf'] * m + gf) / (m + 1)
                team_stats[t]['ga'] = (team_stats[t]['ga'] * m + ga) / (m + 1)
                team_stats[t]['matches'] += 1

    feature_df = pd.DataFrame(processed_rows)
    X_cols = ['H_Roll_GF', 'H_Roll_GA', 'A_Roll_GF', 'A_Roll_GA']
    X = feature_df[X_cols]
    y = feature_df['Target']

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = XGBClassifier(
        n_estimators=150,
        max_depth=4,
        learning_rate=0.05,
        objective='multi:softprob',
        num_class=3,
        random_state=42
    )
    model.fit(X_scaled, y)

    return model, scaler, team_stats

xgb_model, xgb_scaler, team_db = load_and_train_1x2_model()

# ==========================================
# 3. API ODDS FETCH & PARSER
# ==========================================
@st.cache_data(ttl=300, show_spinner=False)
def fetch_1x2_odds(api_key):
    if not api_key:
        return []
    url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds/?apiKey={api_key}&regions=us,uk&markets=h2h"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []

def convert_1x2_odds_to_prob(ho, do, ao):
    if ho <= 1.0 or do <= 1.0 or ao <= 1.0:
        return 33.3, 33.3, 33.3
    raw_h, raw_d, raw_a = 1/ho, 1/do, 1/ao
    margin = raw_h + raw_d + raw_a
    return round((raw_h/margin)*100, 1), round((raw_d/margin)*100, 1), round((raw_a/margin)*100, 1)

# ==========================================
# 4. INTERFACE & FEATURE VECTOR CONSTRUCTION
# ==========================================
st.sidebar.header("⚙️ Feature Engineering & Controls")
odds_key = st.sidebar.text_input("🔑 The Odds API Key (Optional):", type="password")

st.sidebar.markdown("---")
st.sidebar.subheader("⚽ Squad Lineup Index (Feature Weighting)")
h_squad_idx = st.sidebar.slider("Home Squad Fitness Index:", 0.5, 1.2, 1.0, 0.05)
a_squad_idx = st.sidebar.slider("Away Squad Fitness Index:", 0.5, 1.2, 1.0, 0.05)

raw_odds = fetch_1x2_odds(odds_key)
active_matches = [
    {"home": "Real Madrid", "away": "Barcelona", "ho": 2.10, "do": 3.40, "ao": 3.20},
    {"home": "Manchester City", "away": "Arsenal", "ho": 1.95, "do": 3.50, "ao": 3.60},
    {"home": "Liverpool", "away": "Chelsea", "ho": 1.80, "do": 3.80, "ao": 4.00}
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

# Fetch Dynamic Pre-Match Rolling Stats
norm_home = normalize_team_name(curr['home'])
norm_away = normalize_team_name(curr['away'])

h_stats = team_db.get(norm_home, {'gf': 1.8, 'ga': 1.0})
a_stats = team_db.get(norm_away, {'gf': 1.6, 'ga': 1.2})

# Construct ML Feature Vector
raw_vector = np.array([[
    h_stats['gf'] * h_squad_idx,
    h_stats['ga'] / h_squad_idx,
    a_stats['gf'] * a_squad_idx,
    a_stats['ga'] / a_squad_idx
]])

scaled_vector = xgb_scaler.transform(raw_vector)
probs = xgb_model.predict_proba(scaled_vector)[0]

# Class Mapping: [0: Away Win, 1: Draw, 2: Home Win]
ai_prob_a = round(probs[0] * 100, 1)
ai_prob_d = round(probs[1] * 100, 1)
ai_prob_h = round(probs[2] * 100, 1)

mkt_prob_h, mkt_prob_d, mkt_prob_a = convert_1x2_odds_to_prob(curr['ho'], curr['do'], curr['ao'])

# ==========================================
# 5. ANALYTICS & SAFE PROGRESS DISPLAY
# ==========================================
st.divider()
st.subheader(f"📊 1X2 Probabilities: {curr['home']} vs {curr['away']}")

c1, c2, c3 = st.columns(3)
with c1:
    st.write(f"### 🚩 Home ({curr['home']})")
    st.metric("🧠 ML Win %", f"{ai_prob_h}%")
    st.metric("📊 Market %", f"{mkt_prob_h}%")
    st.progress(safe_progress_val(ai_prob_h))

with c2:
    st.write("### ⚖️ Draw (X)")
    st.metric("🧠 ML Draw %", f"{ai_prob_d}%")
    st.metric("📊 Market %", f"{mkt_prob_d}%")
    st.progress(safe_progress_val(ai_prob_d))

with c3:
    st.write(f"### 🚩 Away ({curr['away']})")
    st.metric("🧠 ML Win %", f"{ai_prob_a}%")
    st.metric("📊 Market %", f"{mkt_prob_a}%")
    st.progress(safe_progress_val(ai_prob_a))

st.markdown("---")
edge_h = round(ai_prob_h - mkt_prob_h, 1)
edge_d = round(ai_prob_d - mkt_prob_d, 1)
edge_a = round(ai_prob_a - mkt_prob_a, 1)

if edge_h > 3.0:
    st.success(f"🔥 **VALUE BET FOUND:** ML Model gives **{curr['home']} Win** a **+{edge_h}% Edge** over Market Odds!")
elif edge_d > 3.0:
    st.success(f"🔥 **VALUE BET FOUND:** ML Model gives **DRAW (X)** a **+{edge_d}% Edge** over Market Odds!")
elif edge_a > 3.0:
    st.success(f"🔥 **VALUE BET FOUND:** ML Model gives **{curr['away']} Win** a **+{edge_a}% Edge** over Market Odds!")
else:
    st.info("💡 **Market Balance:** Predictions align with Current Market Odds.")

st.json({
    "Multi-Class Objective": "multi:softprob (3 Classes: Home Win, Draw, Away Win)",
    "Data-Leakage Prevention": "Strict Pre-Match Rolling Averages Engine Active",
    "Normalized Team Keys": f"{norm_home} vs {norm_away}",
    "1X2 Market Value Margins": f"Home ({edge_h}%) | Draw ({edge_d}%) | Away ({edge_a}%)"
})
