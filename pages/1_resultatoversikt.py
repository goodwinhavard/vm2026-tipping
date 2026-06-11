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
st.markdown(
    '<span style="color:green">■ Riktig resultat (3p)</span> &nbsp;'
    '<span style="color:blue">■ Riktig vinner, feil resultat (1p)</span> &nbsp;'
    '<span style="color:red">■ Feil vinner (0p)</span>',
    unsafe_allow_html=True
)

group_rows = []
group_color_rows = []

for i, actual_match in enumerate(actual['matches']):
    played = actual_match['home_score'] != 999 and actual_match['away_score'] != 999
    result = f"{actual_match['home_score']}–{actual_match['away_score']}" if played else "–"
    row = {'#': i + 1, 'Kamp': f"{actual_match['home']} vs {actual_match['away']}", 'Resultat': result}
    color_row = {'#': '', 'Kamp': '', 'Resultat': ''}

    for person in persons:
        col = person.title()
        pred_matches = predictions_data['predictions'][person]['matches']
        if i < len(pred_matches):
            pred = pred_matches[i]
            tip = f"{pred['home_score']}–{pred['away_score']}"
            pts = group_stage_points(pred, actual_match)
            if pts is None:
                color = ''
            elif pts == 0:
                color = 'color: red'
            elif pts == 1:
                color = 'color: blue'
            else:
                color = 'color: green'
            row[col] = tip
            color_row[col] = color
        else:
            row[col] = ''
            color_row[col] = ''

    group_rows.append(row)
    group_color_rows.append(color_row)

group_df = pd.DataFrame(group_rows)
color_df = pd.DataFrame(group_color_rows)
styled_group = group_df.style.apply(lambda _: color_df, axis=None)
st.dataframe(styled_group, use_container_width=True, hide_index=True)

# ── Knockout tips overview ────────────────────────────────────────────────────
def knockout_tips_overview(stage_key, stage_label):
    actual_teams = set(actual.get(stage_key, []))
    all_tips = {p: predictions_data['predictions'][p].get(stage_key, []) for p in persons}
    max_rows = max((len(t) for t in all_tips.values()), default=0)

    if max_rows == 0:
        st.info(f"{stage_label}: ingen tips enda.")
        return

    rows = []
    color_rows = []
    for i in range(max_rows):
        row = {'#': i + 1}
        color_row = {'#': ''}
        for person in persons:
            col = person.title()
            tips = all_tips[person]
            team = tips[i] if i < len(tips) else ''
            row[col] = team
            color_row[col] = 'background-color: #c6efce' if (team and team in actual_teams) else ''
        rows.append(row)
        color_rows.append(color_row)

    df = pd.DataFrame(rows)
    color_df = pd.DataFrame(color_rows)
    styled = df.style.apply(lambda _: color_df, axis=None)
    st.dataframe(styled, use_container_width=True, hide_index=True)


# ── Round of 32 ───────────────────────────────────────────────────────────────
st.header("Runde av 32")
st.caption("Grønn = riktig lag videre · 2 poeng per riktig lag")
knockout_tips_overview('round_of_32', 'Runde av 32')

# ── Round of 16 ───────────────────────────────────────────────────────────────
st.header("Runde av 16")
st.caption("Grønn = riktig lag videre · 4 poeng per riktig lag")
knockout_tips_overview('round_of_16', 'Runde av 16')

# ── Quarter Finals ────────────────────────────────────────────────────────────
st.header("Kvartfinaler")
st.caption("Grønn = riktig lag videre · 8 poeng per riktig lag")
knockout_tips_overview('quarter_finals', 'Kvartfinaler')

# ── Semi Finals ───────────────────────────────────────────────────────────────
st.header("Semifinaler")
st.caption("Grønn = riktig lag videre · 16 poeng per riktig lag")
knockout_tips_overview('semi_finals', 'Semifinaler')

# ── Finals ────────────────────────────────────────────────────────────────────
st.header("Finale")
st.caption("Grønn = riktig finalist (32 poeng) / riktig vinner (64 poeng)")

actual_final_teams = set(actual['finals'].get('teams', []))
actual_winner = actual['finals'].get('winner', '')

labels = ['Finalist 1', 'Finalist 2', 'Vinner']
rows = []
color_rows = []
for i, label in enumerate(labels):
    row = {'Rolle': label}
    color_row = {'Rolle': ''}
    for person in persons:
        col = person.title()
        person_final = predictions_data['predictions'][person].get('finals', {})
        if i < 2:
            teams = person_final.get('teams', [])
            team = teams[i] if i < len(teams) else ''
            row[col] = team
            color_row[col] = 'background-color: #c6efce' if (team and team in actual_final_teams) else ''
        else:
            winner = person_final.get('winner', '')
            row[col] = winner
            color_row[col] = 'background-color: #c6efce' if (winner and winner == actual_winner) else ''
    rows.append(row)
    color_rows.append(color_row)

df = pd.DataFrame(rows)
color_df = pd.DataFrame(color_rows)
styled = df.style.apply(lambda _: color_df, axis=None)
st.dataframe(styled, use_container_width=True, hide_index=True)
