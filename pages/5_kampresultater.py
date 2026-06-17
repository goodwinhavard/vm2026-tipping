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
