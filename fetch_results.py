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
            'round_of_32': ["Mexico", "USA"],
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
            
            # Process matches: Include all Group Stage matches (FINISHED, IN_PLAY, TIMED)
            # and only FINISHED matches for knockout stages to track winners
            if status == 'FINISHED' or (stage == 'GROUP_STAGE' and status in ['IN_PLAY', 'TIMED']):
                home_score = match['score']['fullTime']['home']
                away_score = match['score']['fullTime']['away']
                
                match_result = {
                    'home_team_eng': home_team,
                    'away_team_eng': away_team,
                    'home_team': home_team_nor,
                    'away_team': away_team_nor,
                    'home_score': home_score,
                    'away_score': away_score,
                    'score_str': f"{home_score}–{away_score}" if home_score is not None else "–"
                }
                
                # Add to appropriate list
                if stage == 'GROUP_STAGE':
                    matches.append(match_result)
                elif status == 'FINISHED' and stage in stage_mapping:
                    # Determine winner for knockout stages
                    if home_score > away_score:
                        winner = home_team_nor
                    elif away_score > home_score:
                        winner = away_team_nor
                    else:
                        # For knockout stages, there shouldn't be draws (goes to extra time/penalties)
                        # But if it happens, we'll skip it
                        continue
                    
                    if stage == 'FINAL':
                        knockout_stages['finals_winner'] = winner
                        # Also add both finalists to finals_teams
                        if home_team_nor not in knockout_stages['finals_teams']:
                            knockout_stages['finals_teams'].append(home_team_nor)
                        if away_team_nor not in knockout_stages['finals_teams']:
                            knockout_stages['finals_teams'].append(away_team_nor)
                    else:
                        stage_key = stage_mapping[stage]
                        knockout_stages[stage_key].append(winner)
        
        return {
            'matches': matches,
            'round_of_32': knockout_stages['round_of_32'],
            'round_of_16': knockout_stages['round_of_16'],
            'quarter_finals': knockout_stages['quarter_finals'],
            'semi_finals': knockout_stages['semi_finals'],
            'finals_teams': knockout_stages['finals_teams'],
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
