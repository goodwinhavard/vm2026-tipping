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
st.markdown("# ⚽ VM 2026 - Tippekonkurranse")
st.markdown("---")

# Welcome Section
st.markdown("""
## VM 2026 Tippekonkurransen!

### 🏆 Konkurransestatus

""")

# Load competition status
import json

@st.cache_data
def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

try:
    actual_data = load_json('current_results.json')
    scores_data = load_json('scores.json')
    
    # Count played matches
    played_matches = sum(1 for match in actual_data['predictions']['results']['matches'] 
                         if match['home_score'] != 999 and match['away_score'] != 999)
    total_matches = len(actual_data['predictions']['results']['matches'])
    
    # Get current leader
    sorted_scores = sorted(scores_data.items(), key=lambda x: x[1]['total'], reverse=True)
    leader = sorted_scores[0][0].title() if sorted_scores else "TBD"
    leader_score = sorted_scores[0][1]['total'] if sorted_scores else 0
    
    st.metric("Nåværende leder", leader, f"{leader_score} poeng")

    st.markdown("---")
    st.subheader("🏆 Full Leaderboard")

    leaderboard_data = []
    for rank, (person, data) in enumerate(sorted_scores, 1):
        leaderboard_data.append({
            'Rank': rank,
            'Person': person.title(),
            'Total': data['total'],
            'Group Stage': data['breakdown']['group_stage'],
            'R32': data['breakdown']['round_of_32'],
            'R16': data['breakdown']['round_of_16'],
            'QF': data['breakdown']['quarter_finals'],
            'SF': data['breakdown']['semi_finals'],
            'Finals': data['breakdown']['finals_teams'],
            'Winner': data['breakdown']['finals_winner']
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
