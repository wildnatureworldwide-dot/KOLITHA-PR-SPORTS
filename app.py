import streamlit as st
import pandas as pd

# 1. Mobile Interface Optimization
st.set_page_config(page_title="Live Sports AI Predictor", page_icon="⚽", layout="centered")

st.markdown("<h2 style='text-align: center; color: #38BDF8;'>⚽ Live Sports AI Predictor Pro</h2>", unsafe_allow_html=True)

# 2. Automated Sports Data Collection (Live & Upcoming)
live_matches = [
    {"id": 1, "match": "Real Madrid vs Barcelona", "league": "La Liga", "score": "1 - 1", "time": "62'", "odds_a": 1.80, "odds_b": 2.10, "form_a": 8.5, "form_b": 7.8, "lineup_effect": 3.0},
    {"id": 2, "match": "Man City vs Liverpool", "league": "Premier League", "score": "2 - 0", "time": "35'", "odds_a": 1.55, "odds_b": 2.80, "form_a": 9.0, "form_b": 8.1, "lineup_effect": -2.0},
    {"id": 3, "match": "Bayern Munich vs Dortmund", "league": "Bundesliga", "score": "0 - 0", "time": "12'", "odds_a": 1.65, "odds_b": 2.40, "form_a": 8.2, "form_b": 7.5, "lineup_effect": 0.0},
]

upcoming_matches = [
    {"id": 4, "match": "Arsenal vs Chelsea", "league": "Premier League", "time": "Today, 11:30 PM", "odds_a": 1.95, "odds_b": 2.05, "form_a": 8.0, "form_b": 7.2, "lineup_effect": 1.5},
    {"id": 5, "match": "PSG vs Marseille", "league": "Ligue 1", "time": "Tomorrow, 01:00 AM", "odds_a": 1.40, "odds_b": 3.10, "form_a": 8.8, "form_b": 6.9, "lineup_effect": 0.0},
]

# 3. Prediction Analysis Generator
def show_prediction_details(match_data):
    st.divider()
    team_a, team_b = match_data["match"].split(" vs ")
    
    st.subheader(f"📊 Prediction: {match_data['match']}")
    st.caption(f"League: {match_data['league']}")

    # Probability Calculation
    odds_a, odds_b = match_data["odds_a"], match_data["odds_b"]
    implied_a, implied_b = 1 / odds_a, 1 / odds_b
    total = implied_a + implied_b
    
    win_a = round(((implied_a / total) * 100) + match_data["lineup_effect"], 1)
    win_b = round(100 - win_a, 1)
    
    # Estimated Score Calculation
    score_a = int(round((win_a / 100) * 3))
    score_b = int(round((win_b / 100) * 3))

    # Mobile Cards Grid
    col1, col2 = st.columns(2)
    with col1:
        st.metric(f"🚩 {team_a}", f"{win_a}%")
        st.progress(win_a / 100)
    with col2:
        st.metric(f"🚩 {team_b}", f"{win_b}%")
        st.progress(win_b / 100)

    st.info(f"🎯 **AI Estimated Final Score:** {score_a} - {score_b}")
    
    if win_a > win_b:
        st.success(f"🏆 Highest Winning Chance: **{team_a}**")
    else:
        st.success(f"🏆 Highest Winning Chance: **{team_b}**")

    # Detailed Player & Odds Breakdown Table
    st.write("** Match & Player Details:**")
    df = pd.DataFrame({
        "Metric": ["Live Betting Odds", "Player History Form Rating", "Live Lineup Impact"],
        team_a: [f"{odds_a}", f"{match_data['form_a']}/10", f"+{match_data['lineup_effect']}%"],
        team_b: [f"{odds_b}", f"{match_data['form_b']}/10", f"-{match_data['lineup_effect']}%"]
    })
    st.dataframe(df, use_container_width=True)

# 4. Mobile Tabs Navigation
tab1, tab2 = st.tabs(["🔴 Live Matches", "📅 Upcoming Matches"])

with tab1:
    st.write("ලයිව් පැවැත්වෙන තරඟයක් තෝරන්න:")
    match_options = [f"⚽ {m['match']} [{m['time']} - Score: {m['score']}]" for m in live_matches]
    selected_live = st.selectbox("Choose Live Match", range(len(match_options)), format_func=lambda x: match_options[x])
    
    # Display details for selected match
    show_prediction_details(live_matches[selected_live])

with tab2:
    st.write("ඉදිරියට පැවැත්වෙන තරඟයක් තෝරන්න:")
    upcoming_options = [f"📅 {m['match']} ({m['time']})" for m in upcoming_matches]
    selected_up = st.selectbox("Choose Upcoming Match", range(len(upcoming_options)), format_func=lambda x: upcoming_options[x])
    
    # Display details for selected match
    show_prediction_details(upcoming_matches[selected_up])
