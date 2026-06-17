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
from fetch_results import fetch_world_cup_results

@st.cache_data
def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def ensure_results_loaded():
    """Ensure results are loaded in session state."""
    if 'tournament_results' not in st.session_state or not st.session_state.tournament_results:

        st.session_state.tournament_results = fetch_world_cup_results()



@st.cache_data
def get_scores():
    return calculate_scores()

def get_scores_with_results():
    """Get scores using current results from session state."""
    tournament_results = st.session_state.get('tournament_results', {})
    return calculate_scores(tournament_results=tournament_results)

try:
    # Ensure results are loaded
    ensure_results_loaded()
    
    tournament_results = st.session_state.get('tournament_results', {})
    actual_results = tournament_results.get('matches', [])
    print(len(actual_results))
    scores_data = get_scores_with_results()
    
    # Count played matches (non-zero scores)
    played_matches = sum(1 for match in actual_results 
                         if match['home_score'] is not None and match['away_score'] is not None)
    total_matches = len(actual_results)
    
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

    unplayed_matches = sum(
        1 for m in actual_results
        if m.get('home_score') is None or m.get('away_score') is None or m.get('home_score') == 999 or m.get('away_score') == 999
    )

    predictions_data = load_json('all_tournament_tips.json')

    # Stages in elimination order, with their full-size thresholds
    _stage_order = ['round_of_32', 'round_of_16', 'quarter_finals', 'semi_finals', 'finals_teams']
    _stage_sizes = {'round_of_32': 32, 'round_of_16': 16, 'quarter_finals': 8, 'semi_finals': 4, 'finals_teams': 2}

    def is_team_eliminated(team, for_stage):
        """True if team is confirmed out before reaching for_stage."""
        if for_stage == 'finals_winner':
            finals_teams = tournament_results.get('finals_teams') or []
            if len(finals_teams) == 2:
                return team not in finals_teams
            preceding = _stage_order
        else:
            preceding = _stage_order[:_stage_order.index(for_stage)]
        for sk in preceding:
            actual = tournament_results.get(sk) or []
            if len(actual) == _stage_sizes[sk] and team not in actual:
                return True
        return False

    def max_potential(breakdown, player_prediction):
        add = unplayed_matches * 3
        knockout_stages = [
            ('round_of_32', 32, 2),
            ('round_of_16', 16, 4),
            ('quarter_finals', 8, 8),
            ('semi_finals', 4, 16),
            ('finals_teams', 2, 32),
            ('finals_winner', 1, 64),
        ]
        for stage_key, total_slots, pts in knockout_stages:
            if stage_key == 'finals_winner':
                actual_set = {tournament_results.get('finals_winner')} - {None}
                pred_teams = [player_prediction.get('finals', {}).get('winner')] if player_prediction.get('finals', {}).get('winner') else []
            elif stage_key == 'finals_teams':
                actual_set = set(tournament_results.get('finals_teams') or [])
                pred_teams = list(player_prediction.get('finals', {}).get('teams') or [])
            else:
                actual_set = set(tournament_results.get(stage_key) or [])
                pred_teams = list(player_prediction.get(stage_key) or [])
            remaining_slots = max(0, total_slots - len(actual_set))
            unscored = [t for t in pred_teams if t and t not in actual_set]
            still_alive = [t for t in unscored if not is_team_eliminated(t, stage_key)]
            add += min(len(still_alive), remaining_slots) * pts
            #print(stage_key, actual_set, pred_teams, unscored, still_alive, add)
        return breakdown['total'] + add

    leaderboard_data = []
    for rank, (person, data) in enumerate(sorted_scores, 1):
        breakdown = data['breakdown']
        player_prediction = predictions_data['predictions'].get(person, {})
        leaderboard_data.append({
            'Rank': rank,
            'Person': person.title(),
            'Total': data['total'],
            'Maks Mulig poeng': max_potential(breakdown, player_prediction),
            'Group Stage': breakdown['group_stage'],
            'R32': breakdown['round_of_32'],
            'R16': breakdown['round_of_16'],
            'QF': breakdown['quarter_finals'],
            'SF': breakdown['semi_finals'],
            'Finals': breakdown['finals_teams'],
            'Winner': breakdown['finals_winner']
        })

    leaderboard_df = pd.DataFrame(leaderboard_data)
    st.dataframe(leaderboard_df, width='stretch', hide_index=True)
        
except Exception as e:
    st.error(f"Error loading scores or results: {e}")
    

st.markdown("---")

st.markdown("""

### 🔄 Sist oppdatert

""" + datetime.now().strftime("%Y-%m-%d %H:%M") + """

""")
