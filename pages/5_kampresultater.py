import streamlit as st
import sys
import os
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from fetch_results import fetch_world_cup_results

st.title("⚽ Kampresultater")
st.markdown("---")

if 'tournament_results' not in st.session_state or not st.session_state.tournament_results:
    st.info("Laster resultater...")
    # This might trigger a reload, but ensures data is present if page is accessed directly
    # or session state is cleared. A more robust solution might involve ensure_results_loaded()
    # from hovedside.py, but for a single page, a direct call is acceptable.
    st.session_state.tournament_results = fetch_world_cup_results()

all_matches = st.session_state.tournament_results.get('matches', [])

played_matches_data = []
for match in all_matches:
    #if match['home_score'] is not None and match['away_score'] is not None and match['home_score'] != 999 and match['away_score'] != 999:
    played_matches_data.append({'Hjemmelag': match['home_team'], 'Resultat': match['score_str'], 'Bortelag': match['away_team']})

if played_matches_data:
    df = pd.DataFrame(played_matches_data)
    st.dataframe(df, hide_index=True, width='stretch')
else:
    st.info("Ingen ferdigstilte kamper å vise.")

st.markdown("---")
st.subheader("Videre til sluttspillet")

round_of_32 = st.session_state.tournament_results.get('round_of_32', [])
round_of_16 = st.session_state.tournament_results.get('round_of_16', [])
quarter_finals = st.session_state.tournament_results.get('quarter_finals', [])
semi_finals = st.session_state.tournament_results.get('semi_finals', [])
finals_teams = st.session_state.tournament_results.get('finals_teams', [])
finals_winner = st.session_state.tournament_results.get('finals_winner')

def team_list(teams, empty_msg="Ikke avgjort ennå"):
    if teams:
        for t in teams:
            st.write(f"- {t}")
    else:
        st.caption(empty_msg)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown("**Runde av 32**")
    team_list(round_of_32)

with col2:
    st.markdown("**Runde av 16**")
    team_list(round_of_16)

with col3:
    st.markdown("**Kvartfinale**")
    team_list(quarter_finals)

with col4:
    st.markdown("**Semifinale**")
    team_list(semi_finals)

with col5:
    st.markdown("**Finale**")
    team_list(finals_teams)
    if finals_winner:
        st.markdown(f"**Vinner: {finals_winner}**")
