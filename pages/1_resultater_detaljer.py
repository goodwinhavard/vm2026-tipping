import streamlit as st
import json
import pandas as pd
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Results - World Cup 2026 Tipping",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
@st.cache_data
def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

scores_data = load_json('scores.json')
predictions_data = load_json('all_tournament_tips.json')
actual_data = load_json('real_results.json')

# Title and Header
st.markdown("# 🏆 Competition Results")
st.markdown("---")

# Main Leaderboard
col1, col2, col3 = st.columns(3)

sorted_scores = sorted(scores_data.items(), key=lambda x: x[1]['total'], reverse=True)

with col1:
    st.metric("🥇 Leader", sorted_scores[0][0].title(), f"{sorted_scores[0][1]['total']} pts")
if len(sorted_scores) > 1:
    with col2:
        st.metric("🥈 Second", sorted_scores[1][0].title(), f"{sorted_scores[1][1]['total']} pts")
if len(sorted_scores) > 2:
    with col3:
        st.metric("🥉 Third", sorted_scores[2][0].title(), f"{sorted_scores[2][1]['total']} pts")

st.markdown("---")

# Tournament Progress Section
st.subheader("📊 Tournament Progress")

# Count played matches (not 999)
played_matches = sum(1 for match in actual_data['predictions']['results']['matches'] 
                     if match['home_score'] != 999 and match['away_score'] != 999)
total_matches = len(actual_data['predictions']['results']['matches'])

# Count completed stages
round32 = len([t for t in actual_data['predictions']['results']['round_of_32'] if t])
round16 = len([t for t in actual_data['predictions']['results']['round_of_16'] if t])
qf = len([t for t in actual_data['predictions']['results']['quarter_finals'] if t])
sf = len([t for t in actual_data['predictions']['results']['semi_finals'] if t])
finals = len([t for t in actual_data['predictions']['results']['finals']['teams'] if t])

progress_col1, progress_col2, progress_col3 = st.columns(3)
with progress_col1:
    st.metric("Group Stage", f"{played_matches}/{total_matches} matches", f"{int(played_matches/total_matches*100)}%")
with progress_col2:
    stages_complete = sum([bool(round32), bool(round16), bool(qf), bool(sf), bool(finals)])
    st.metric("Knockout Stages", f"{stages_complete}/5 complete")
with progress_col3:
    if finals:
        winner = actual_data['predictions']['results']['finals']['winner']
        st.metric("🏆 Current Champion", winner if winner else "TBD")

st.markdown("---")

# Full Leaderboard Table
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

st.markdown("---")

# Detailed View Section
st.subheader("🔍 Detailed Results Per Person")

selected_person = st.selectbox(
    "Select a person to view detailed results:",
    [person.title() for person, _ in sorted_scores]
)

selected_person_lower = selected_person.lower()

# Find the person in predictions data
person_pred = predictions_data['predictions'].get(selected_person_lower, {})
person_scores = scores_data.get(selected_person_lower, {})

if person_pred and person_scores:
    # Score breakdown
    st.markdown(f"### {selected_person} - Total: {person_scores['total']} points")
    
    breakdown = person_scores['breakdown']
    
    # Breakdown visualization
    breakdown_col1, breakdown_col2, breakdown_col3, breakdown_col4 = st.columns(4)
    with breakdown_col1:
        st.metric("Group Stage", f"{breakdown['group_stage']} pts")
    with breakdown_col2:
        st.metric("R32-Finals", f"{breakdown['round_of_32'] + breakdown['round_of_16'] + breakdown['quarter_finals'] + breakdown['semi_finals'] + breakdown['finals_teams']} pts")
    with breakdown_col3:
        st.metric("Finals Winner", f"{breakdown['finals_winner']} pts")
    with breakdown_col4:
        st.metric("Total", f"{breakdown['total']} pts")
    
    st.markdown("---")
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Group Stage Matches", "Knockout Predictions", "Comparison", "Summary"])
    
    with tab1:
        st.markdown("#### Group Stage Match Results")
        st.markdown(f"**Scored: {breakdown['group_stage']} points**")
        
        # Create a table of group stage matches
        group_stage_data = []
        for i, pred_match in enumerate(person_pred['matches']):
            actual_match = actual_data['predictions']['results']['matches'][i]
            
            # Check if match is played
            if actual_match['home_score'] == 999 or actual_match['away_score'] == 999:
                status = "Not played"
                points = 0
                score_display = f"{pred_match['home_score']}-{pred_match['away_score']} vs TBD"
            else:
                # Calculate points
                points = 0
                if pred_match['home_score'] > pred_match['away_score']:
                    pred_winner = 'home'
                elif pred_match['away_score'] > pred_match['home_score']:
                    pred_winner = 'away'
                else:
                    pred_winner = 'draw'
                
                if actual_match['home_score'] > actual_match['away_score']:
                    actual_winner = 'home'
                elif actual_match['away_score'] > actual_match['home_score']:
                    actual_winner = 'away'
                else:
                    actual_winner = 'draw'
                
                if pred_winner == actual_winner:
                    points = 1
                    if pred_match['home_score'] == actual_match['home_score'] and pred_match['away_score'] == actual_match['away_score']:
                        points = 3
                    status = "✓ Correct"
                else:
                    status = "✗ Wrong"
                
                score_display = f"{pred_match['home_score']}-{pred_match['away_score']} vs {actual_match['home_score']}-{actual_match['away_score']}"
            
            group_stage_data.append({
                'Match': f"{pred_match['home']} vs {pred_match['away']}",
                'Prediction': f"{pred_match['home_score']}-{pred_match['away_score']}",
                'Actual': f"{actual_match['home_score']}-{actual_match['away_score']}" if actual_match['home_score'] != 999 else "TBD",
                'Status': status,
                'Points': points
            })
        
        group_df = pd.DataFrame(group_stage_data)
        st.dataframe(group_df, use_container_width=True, hide_index=True)
    
    with tab2:
        st.markdown("#### Knockout Stage Predictions")
        
        knockout_col1, knockout_col2 = st.columns(2)
        
        with knockout_col1:
            st.markdown(f"**Round of 32 ({len(person_pred['round_of_32'])} teams)**")
            r32_correct = len(set(person_pred['round_of_32']) & set(actual_data['predictions']['results']['round_of_32']))
            st.write(f"Correct: {r32_correct}/{len(person_pred['round_of_32'])} → {r32_correct * 2} points")
            
            with st.expander("View teams"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write("**Predicted:**")
                    for team in person_pred['round_of_32']:
                        st.write(f"• {team}")
                with col_b:
                    st.write("**Actual:**")
                    for team in actual_data['predictions']['results']['round_of_32']:
                        if team:
                            st.write(f"• {team}")
            
            st.markdown(f"**Round of 16 ({len(person_pred['round_of_16'])} teams)**")
            r16_correct = len(set(person_pred['round_of_16']) & set(actual_data['predictions']['results']['round_of_16']))
            st.write(f"Correct: {r16_correct}/{len(person_pred['round_of_16'])} → {r16_correct * 4} points")
            
            with st.expander("View teams"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write("**Predicted:**")
                    for team in person_pred['round_of_16']:
                        st.write(f"• {team}")
                with col_b:
                    st.write("**Actual:**")
                    for team in actual_data['predictions']['results']['round_of_16']:
                        if team:
                            st.write(f"• {team}")
        
        with knockout_col2:
            st.markdown(f"**Quarter Finals ({len(person_pred['quarter_finals'])} teams)**")
            qf_correct = len(set(person_pred['quarter_finals']) & set(actual_data['predictions']['results']['quarter_finals']))
            st.write(f"Correct: {qf_correct}/{len(person_pred['quarter_finals'])} → {qf_correct * 8} points")
            
            with st.expander("View teams"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write("**Predicted:**")
                    for team in person_pred['quarter_finals']:
                        st.write(f"• {team}")
                with col_b:
                    st.write("**Actual:**")
                    for team in actual_data['predictions']['results']['quarter_finals']:
                        if team:
                            st.write(f"• {team}")
            
            st.markdown(f"**Semi Finals ({len(person_pred['semi_finals'])} teams)**")
            sf_correct = len(set(person_pred['semi_finals']) & set(actual_data['predictions']['results']['semi_finals']))
            st.write(f"Correct: {sf_correct}/{len(person_pred['semi_finals'])} → {sf_correct * 16} points")
            
            with st.expander("View teams"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write("**Predicted:**")
                    for team in person_pred['semi_finals']:
                        st.write(f"• {team}")
                with col_b:
                    st.write("**Actual:**")
                    for team in actual_data['predictions']['results']['semi_finals']:
                        if team:
                            st.write(f"• {team}")
        
        # Finals
        st.markdown("**Finals**")
        finals_col1, finals_col2 = st.columns(2)
        with finals_col1:
            st.write(f"**Predicted:** {person_pred['finals']['teams'][0]} vs {person_pred['finals']['teams'][1] if len(person_pred['finals']['teams']) > 1 else 'TBD'}")
            st.write(f"**Actual:** {actual_data['predictions']['results']['finals']['teams'][0] if actual_data['predictions']['results']['finals']['teams'] else 'TBD'} vs {actual_data['predictions']['results']['finals']['teams'][1] if len(actual_data['predictions']['results']['finals']['teams']) > 1 else 'TBD'}")
        with finals_col2:
            st.write(f"**Predicted Winner:** {person_pred['finals']['winner']}")
            st.write(f"**Actual Winner:** {actual_data['predictions']['results']['finals']['winner'] if actual_data['predictions']['results']['finals']['winner'] else 'TBD'}")
            finals_winner_correct = person_pred['finals']['winner'] == actual_data['predictions']['results']['finals']['winner']
            st.write(f"**Points:** {64 if finals_winner_correct else 0}")
    
    with tab3:
        st.markdown("#### Comparison with Other Predictions")
        
        # Compare knockout predictions
        comparison_data = {
            'Person': [],
            'R32 Correct': [],
            'R16 Correct': [],
            'QF Correct': [],
            'SF Correct': [],
            'Finals Winner': []
        }
        
        for person, pred in predictions_data['predictions'].items():
            comparison_data['Person'].append(person.title())
            comparison_data['R32 Correct'].append(
                len(set(pred['round_of_32']) & set(actual_data['predictions']['results']['round_of_32']))
            )
            comparison_data['R16 Correct'].append(
                len(set(pred['round_of_16']) & set(actual_data['predictions']['results']['round_of_16']))
            )
            comparison_data['QF Correct'].append(
                len(set(pred['quarter_finals']) & set(actual_data['predictions']['results']['quarter_finals']))
            )
            comparison_data['SF Correct'].append(
                len(set(pred['semi_finals']) & set(actual_data['predictions']['results']['semi_finals']))
            )
            comparison_data['Finals Winner'].append(
                "✓" if pred['finals']['winner'] == actual_data['predictions']['results']['finals']['winner'] else "✗"
            )
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    with tab4:
        st.markdown("#### Score Summary")
        st.write(f"""
        **{selected_person}** earned their {person_scores['total']} points as follows:
        
        - **Group Stage:** {breakdown['group_stage']} points (Correct match outcomes and scores)
        - **Round of 32:** {breakdown['round_of_32']} points ({breakdown['round_of_32']} ÷ 2 = {breakdown['round_of_32'] // 2 if breakdown['round_of_32'] > 0 else 0} teams correct)
        - **Round of 16:** {breakdown['round_of_16']} points ({breakdown['round_of_16']} ÷ 4 = {breakdown['round_of_16'] // 4 if breakdown['round_of_16'] > 0 else 0} teams correct)
        - **Quarter Finals:** {breakdown['quarter_finals']} points ({breakdown['quarter_finals']} ÷ 8 = {breakdown['quarter_finals'] // 8 if breakdown['quarter_finals'] > 0 else 0} teams correct)
        - **Semi Finals:** {breakdown['semi_finals']} points ({breakdown['semi_finals']} ÷ 16 = {breakdown['semi_finals'] // 16 if breakdown['semi_finals'] > 0 else 0} teams correct)
        - **Finals Teams:** {breakdown['finals_teams']} points ({breakdown['finals_teams']} ÷ 32 = {breakdown['finals_teams'] // 32 if breakdown['finals_teams'] > 0 else 0} teams correct)
        - **Finals Winner:** {breakdown['finals_winner']} points (Correctly predicted champion)
        
        **Total: {breakdown['total']} points**
        """)
