"""Utility module for fetching World Cup results from football-data.org API."""

import requests
import json
import sys
import os
import streamlit as st
from names_eng_to_nor import ENGLISH_TO_NORWEGIAN

@st.cache_data
def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)



def fetch_world_cup_results():
    """
    Fetch World Cup results from football-data.org API
    Returns a complete tournament results dict with group stage matches and knockout stages
    """
    uri = 'https://api.football-data.org/v4/competitions/WC/matches'
    headers = {'X-Auth-Token': 'b006736168e34387975ae15e83b341a4'}
    
    try:
        # Fetch data from API
        response = requests.get(uri, headers=headers, timeout=10)
        response.raise_for_status()
        
        matches = []
        knockout_stages = {
            'round_of_32': ["Mexico", "USA", "Tyskland", "Argentina", "Frankrike", "Norge", "Colombia"],
            'round_of_16': [],
            'quarter_finals': [],
            'semi_finals': [],
            'finals_teams': [],
            'finals_winner': None
        }

        # Stage mapping from API to our format
        stage_mapping = {
            'LAST_32': 'round_of_32',
            'LAST_16': 'round_of_16',
            'QUARTER_FINALS': 'quarter_finals',
            'SEMI_FINALS': 'semi_finals',
            'FINAL': 'finals'
        }

        # Parse JSON response
        for match in response.json()['matches']:
            home_team = match['homeTeam']['name']
            away_team = match['awayTeam']['name']
            stage = match.get('stage', 'GROUP_STAGE')
            status = match.get('status')

            # Convert team names to Norwegian
            home_team_nor = ENGLISH_TO_NORWEGIAN.get(home_team, home_team)
            away_team_nor = ENGLISH_TO_NORWEGIAN.get(away_team, away_team)

            if stage == 'GROUP_STAGE' and status in ['FINISHED', 'IN_PLAY', 'TIMED']:
                home_score = match['score']['fullTime']['home']
                away_score = match['score']['fullTime']['away']
                matches.append({
                    'home_team_eng': home_team,
                    'away_team_eng': away_team,
                    'home_team': home_team_nor,
                    'away_team': away_team_nor,
                    'home_score': home_score,
                    'away_score': away_score,
                    'score_str': f"{home_score}–{away_score}" if home_score is not None else "–"
                })
            elif stage in stage_mapping:
                # Add both participating teams to their stage list regardless of match status,
                # so the list reflects all scheduled/played teams, not just winners.
                if stage == 'FINAL':
                    if home_team_nor not in knockout_stages['finals_teams']:
                        knockout_stages['finals_teams'].append(home_team_nor)
                    if away_team_nor not in knockout_stages['finals_teams']:
                        knockout_stages['finals_teams'].append(away_team_nor)
                    if status == 'FINISHED':
                        home_score = match['score']['fullTime']['home']
                        away_score = match['score']['fullTime']['away']
                        if home_score > away_score:
                            knockout_stages['finals_winner'] = home_team_nor
                        elif away_score > home_score:
                            knockout_stages['finals_winner'] = away_team_nor
                else:
                    stage_key = stage_mapping[stage]
                    if home_team_nor not in knockout_stages[stage_key]:
                        knockout_stages[stage_key].append(home_team_nor)
                    if away_team_nor not in knockout_stages[stage_key]:
                        knockout_stages[stage_key].append(away_team_nor)
        
        return {
            'matches': matches,
            'round_of_32': list(set(knockout_stages['round_of_32'])),
            'round_of_16': list(set(knockout_stages['round_of_16'])),
            'quarter_finals': list(set(knockout_stages['quarter_finals'])),
            'semi_finals': list(set(knockout_stages['semi_finals'])),
            'finals_teams': list(set(knockout_stages['finals_teams'])),
            'finals_winner': knockout_stages['finals_winner']
        }
    
    except Exception as e:
        print("Falling back to local results file...")
        actual_data = load_json('real_results.json')
        raw = actual_data.get('predictions', {}).get('results', {})
        finals = raw.get('finals', {})
        nor_to_eng = {v: k for k, v in ENGLISH_TO_NORWEGIAN.items()}
        matches = []
        for m in raw.get('matches', []):
            home_nor = m.get('home', '')
            away_nor = m.get('away', '')
            home_score = m.get('home_score')
            away_score = m.get('away_score')
            matches.append({
                'home_team': home_nor,
                'away_team': away_nor,
                'home_team_eng': nor_to_eng.get(home_nor, home_nor),
                'away_team_eng': nor_to_eng.get(away_nor, away_nor),
                'home_score': home_score,
                'away_score': away_score,
                'score_str': f"{home_score}–{away_score}" if home_score is not None else "–",
            })
        return {
            'matches': matches,
            'round_of_32': raw.get('round_of_32', []),
            'round_of_16': raw.get('round_of_16', []),
            'quarter_finals': raw.get('quarter_finals', []),
            'semi_finals': raw.get('semi_finals', []),
            'finals_teams': finals.get('teams', []),
            'finals_winner': finals.get('winner') or None,
        }


def fetch_eliminated_teams(results=None):
    """Derive teams eliminated at each stage from tournament results."""
    if results is None:
        results = fetch_world_cup_results()

    r32   = set(results.get('round_of_32') or [])
    r16   = set(results.get('round_of_16') or [])
    qf    = set(results.get('quarter_finals') or [])
    sf    = set(results.get('semi_finals') or [])
    final = set(results.get('finals_teams') or [])
    winner = results.get('finals_winner')

    # Group stage: manually maintained (full 48-team list not in API response)
    pre_round_of_32 = ["Tyrkia"]

    # return {
    #     'pre_round_of_32':    pre_round_of_32,
    #     'pre_round_of_16':    sorted(t for t in r32  if t not in r16),
    #     'pre_quarter_finals': sorted(t for t in r16  if t not in qf),
    #     'pre_semi_finals':    sorted(t for t in qf   if t not in sf),
    #     'pre_finals_teams':   sorted(t for t in sf   if t not in final),
    #     'runner_up':          sorted(t for t in final if t != winner) if winner else [],
    # }

    return {
        'pre_round_of_32':    ["Tyrkia", "Haiti", "Tunisia", "Jordan", "Panama"],
        'pre_round_of_16':    [],
        'pre_quarter_finals': [],
        'pre_semi_finals':    [],
        'pre_finals_teams':   [],
        'runner_up':          [],
    }