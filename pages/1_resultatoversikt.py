import streamlit as st
import json
import pandas as pd

st.set_page_config(
    page_title="Resultater oversikt - VM 2026 Tipping",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

predictions_data = load_json('all_tournament_tips.json')
actual_data = load_json('real_results.json')

persons = list(predictions_data['predictions'].keys())
actual = actual_data['predictions']['results']


def match_outcome(home_score, away_score):
    if home_score > away_score:
        return 'home'
    elif away_score > home_score:
        return 'away'
    return 'draw'


def group_stage_points(pred_match, actual_match):
    if actual_match['home_score'] == 999 or actual_match['away_score'] == 999:
        return None  # not played
    pred_outcome = match_outcome(pred_match['home_score'], pred_match['away_score'])
    actual_outcome = match_outcome(actual_match['home_score'], actual_match['away_score'])
    if pred_outcome != actual_outcome:
        return 0
    if pred_match['home_score'] == actual_match['home_score'] and pred_match['away_score'] == actual_match['away_score']:
        return 3
    return 1


KNOCKOUT_POINTS = {
    'round_of_32': 2,
    'round_of_16': 4,
    'quarter_finals': 8,
    'semi_finals': 16,
    'finals_teams': 32,
    'finals_winner': 64,
}

st.title("VM 2026 – Resultater oversikt")

# ── Group Stage ──────────────────────────────────────────────────────────────
st.header("Gruppespill – 72 kamper")

group_rows = []
for i, actual_match in enumerate(actual['matches']):
    played = actual_match['home_score'] != 999 and actual_match['away_score'] != 999
    result = f"{actual_match['home_score']}–{actual_match['away_score']}" if played else "–"
    row = {
        '#': i + 1,
        'Kamp': f"{actual_match['home']} vs {actual_match['away']}",
        'Resultat': result,
    }
    for person in persons:
        pred_matches = predictions_data['predictions'][person]['matches']
        if i < len(pred_matches):
            pts = group_stage_points(pred_matches[i], actual_match)
            row[person.title()] = '' if pts is None else pts
        else:
            row[person.title()] = ''
    group_rows.append(row)

group_df = pd.DataFrame(group_rows)
st.dataframe(group_df, use_container_width=True, hide_index=True)

# ── Knockout helper ──────────────────────────────────────────────────────────
def knockout_table(stage_key, stage_label, points_per_team):
    actual_teams = actual.get(stage_key, [])
    if not actual_teams:
        st.info(f"{stage_label}: ingen lag enda.")
        return

    rows = []
    for team in actual_teams:
        row = {'Lag': team}
        for person in persons:
            person_teams = predictions_data['predictions'][person].get(stage_key, [])
            row[person.title()] = points_per_team if team in person_teams else 0
        rows.append(row)

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


# ── Round of 32 ───────────────────────────────────────────────────────────────
st.header("Runde av 32")
knockout_table('round_of_32', 'Runde av 32', KNOCKOUT_POINTS['round_of_32'])

# ── Round of 16 ───────────────────────────────────────────────────────────────
st.header("Runde av 16")
knockout_table('round_of_16', 'Runde av 16', KNOCKOUT_POINTS['round_of_16'])

# ── Quarter Finals ────────────────────────────────────────────────────────────
st.header("Kvartfinaler")
knockout_table('quarter_finals', 'Kvartfinaler', KNOCKOUT_POINTS['quarter_finals'])

# ── Semi Finals ───────────────────────────────────────────────────────────────
st.header("Semifinaler")
knockout_table('semi_finals', 'Semifinaler', KNOCKOUT_POINTS['semi_finals'])

# ── Finals ────────────────────────────────────────────────────────────────────
st.header("Finale")

actual_final_teams = actual['finals']['teams']
actual_winner = actual['finals'].get('winner', '')

if actual_final_teams:
    rows = []
    for team in actual_final_teams:
        row = {'Lag': team, 'Rolle': 'Vinner' if team == actual_winner else 'Finalist'}
        for person in persons:
            person_final = predictions_data['predictions'][person]['finals']
            pts = 0
            if team in person_final.get('teams', []):
                pts += KNOCKOUT_POINTS['finals_teams']
            if actual_winner and team == actual_winner and person_final.get('winner') == actual_winner:
                pts += KNOCKOUT_POINTS['finals_winner']
            row[person.title()] = pts
        rows.append(row)

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.info("Finale: ingen lag enda.")
