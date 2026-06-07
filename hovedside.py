import streamlit as st
from datetime import datetime
import pandas as pd

# Set page config
st.set_page_config(
    page_title="VM 2026 Tippekonkurranse",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.markdown("# ⚽ VM 2026 - Tippekonkurranse Forettningsstyring + Tribe 🏆")
st.markdown("---")

# Load competition status
import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from calculate_score import calculate_scores

@st.cache_data
def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

@st.cache_data
def get_scores():
    return calculate_scores()

try:
    actual_data = load_json('real_results.json')
    scores_data = get_scores()
    
    # Count played matches
    played_matches = sum(1 for match in actual_data['predictions']['results']['matches'] 
                         if match['home_score'] != 999 and match['away_score'] != 999)
    total_matches = len(actual_data['predictions']['results']['matches'])
    
    sorted_scores = sorted(scores_data.items(), key=lambda x: x[1]['total'], reverse=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🥇 Leder", sorted_scores[0][0].title(), f"{sorted_scores[0][1]['total']} pts")
    if len(sorted_scores) > 1:
        with col2:
            st.metric("🥈 Andre", sorted_scores[1][0].title(), f"{sorted_scores[1][1]['total']} pts")
    if len(sorted_scores) > 2:
        with col3:
            st.metric("🥉 Tredje", sorted_scores[2][0].title(), f"{sorted_scores[2][1]['total']} pts")

    st.markdown("---")
    st.subheader("🏆 Tabell")

    actual_results = actual_data['predictions']['results']

    def _actual_list(key):
        val = actual_results.get(key, [])
        return [val] if (val and not isinstance(val, list)) else (val or [])

    unplayed_matches = sum(
        1 for m in actual_results['matches']
        if m['home_score'] == 999 or m['away_score'] == 999
    )

    knockout_stages = [
        ('round_of_32', 32),
        ('round_of_16', 16),
        ('quarter_finals', 8),
        ('semi_finals', 4),
    ]

    def max_potential(breakdown):
        add = unplayed_matches * 3
        for stage_key, total_teams in knockout_stages:
            if len(_actual_list(stage_key)) < total_teams:
                add += max(0, 64 - breakdown[stage_key])
        finals = actual_results.get('finals', {})
        if len(finals.get('teams', [])) < 2:
            add += max(0, 64 - breakdown['finals_teams'])
        if not finals.get('winner', ''):
            add += max(0, 64 - breakdown['finals_winner'])
        return breakdown['total'] + add

    leaderboard_data = []
    for rank, (person, data) in enumerate(sorted_scores, 1):
        breakdown = data['breakdown']
        leaderboard_data.append({
            'Rank': rank,
            'Person': person.title(),
            'Total': data['total'],
            'Maks Mulig poeng': max_potential(breakdown),
            'Group Stage': breakdown['group_stage'],
            'R32': breakdown['round_of_32'],
            'R16': breakdown['round_of_16'],
            'QF': breakdown['quarter_finals'],
            'SF': breakdown['semi_finals'],
            'Finals': breakdown['finals_teams'],
            'Winner': breakdown['finals_winner']
        })

    leaderboard_df = pd.DataFrame(leaderboard_data)
    st.dataframe(leaderboard_df, use_container_width=True, hide_index=True)
        
except:
    st.warning("Konkurransedata er ikke lastet ennå. Vær sikker på at alle JSON-filer er tilstede.")

st.markdown("---")

st.markdown("""

### 🔄 Sist oppdatert

""" + (actual_data['extraction_date'][:10] if 'extraction_date' in actual_data else "Ukjent") + """

""")
