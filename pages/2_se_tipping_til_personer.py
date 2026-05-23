import streamlit as st
import json
import pandas as pd

# Set page config
st.set_page_config(
    page_title="View Predictions - World Cup 2026",
    page_icon="👀",
    layout="wide"
)

st.markdown("# 👀 View Predictions")
st.markdown("Select a person to view their complete predictions")
st.markdown("---")

# Load data
@st.cache_data
def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

predictions_data = load_json('all_tournament_results.json')

# Get list of people
people = sorted(predictions_data['predictions'].keys())

# Dropdown to select person
selected_person = st.selectbox(
    "Select a person:",
    people,
    format_func=lambda x: x.title()
)

# Get selected person's data
person_data = predictions_data['predictions'][selected_person]

st.markdown(f"## {selected_person.title()}'s Predictions")
st.markdown("---")

# Group Stage Section
with st.expander("📋 GROUP STAGE MATCHES", expanded=True):
    st.markdown(f"**Total matches: {len(person_data['matches'])}**")
    
    # Create a table of group stage matches
    group_stage_list = []
    for i, match in enumerate(person_data['matches'], 1):
        group_stage_list.append({
            '#': i,
            'Home Team': match['home'],
            'Score': f"{match['home_score']} - {match['away_score']}",
            'Away Team': match['away']
        })
    
    group_df = pd.DataFrame(group_stage_list)
    st.dataframe(group_df, use_container_width=True, hide_index=True)

# Round of 32 Section
with st.expander(f"🏆 ROUND OF 32 ({len(person_data['round_of_32'])} teams)"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Teams:**")
        for i, team in enumerate(person_data['round_of_32'], 1):
            st.write(f"{i:2d}. {team}")
    
    with col2:
        st.markdown("**Summary:**")
        st.info(f"Total teams predicted: {len(person_data['round_of_32'])}")

# Round of 16 Section
with st.expander(f"🥈 ROUND OF 16 ({len(person_data['round_of_16'])} teams)"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Teams:**")
        for i, team in enumerate(person_data['round_of_16'], 1):
            st.write(f"{i:2d}. {team}")
    
    with col2:
        st.markdown("**Summary:**")
        st.info(f"Total teams predicted: {len(person_data['round_of_16'])}")

# Quarter Finals Section
with st.expander(f"⚔️ QUARTER FINALS ({len(person_data['quarter_finals'])} teams)"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Teams:**")
        for i, team in enumerate(person_data['quarter_finals'], 1):
            st.write(f"{i:2d}. {team}")
    
    with col2:
        st.markdown("**Summary:**")
        st.info(f"Total teams predicted: {len(person_data['quarter_finals'])}")

# Semi Finals Section
with st.expander(f"🏅 SEMI FINALS ({len(person_data['semi_finals'])} teams)"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Teams:**")
        for i, team in enumerate(person_data['semi_finals'], 1):
            st.write(f"{i:2d}. {team}")
    
    with col2:
        st.markdown("**Summary:**")
        st.info(f"Total teams predicted: {len(person_data['semi_finals'])}")

# Finals Section
with st.expander("🏆 FINALS & WINNER", expanded=False):
    st.markdown("### Finalists")
    finals_col1, finals_col2 = st.columns(2)
    
    with finals_col1:
        st.metric("Team 1", person_data['finals']['teams'][0] if person_data['finals']['teams'] else "N/A")
    with finals_col2:
        st.metric("Team 2", person_data['finals']['teams'][1] if len(person_data['finals']['teams']) > 1 else "N/A")
    
    st.markdown("### Champion")
    st.metric("🏆 Predicted Winner", person_data['finals']['winner'])
    
    if person_data['finals']['scores']:
        st.markdown("### Final Score")
        score_col1, score_col2 = st.columns(2)
        with score_col1:
            st.metric("Team 1 Score", person_data['finals']['scores'][0] if person_data['finals']['scores'] else "N/A")
        with score_col2:
            st.metric("Team 2 Score", person_data['finals']['scores'][1] if len(person_data['finals']['scores']) > 1 else "N/A")

st.markdown("---")

# Raw JSON View (Optional)
with st.expander("📄 Raw JSON Data"):
    st.json(person_data)
