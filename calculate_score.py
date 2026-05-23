# score group stage. Correct winner (home, away, draw) = 1 point. Correct score = 2 extra points.
# correct number of teams in round of 32 = 2 points per team
# Correct number of teams in round of 16 = 4 points per team.
# Correct number of teams in quarter finals = 8 points per team.
# Correct number of teams in semi finals = 16 points per team.
# Correct number of teams in final = 32 points per team.
# Correct winner of the final = 64 points.

import json

def load_json(filename):
    """Load JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)

def determine_winner(home_score, away_score):
    """Determine match winner: 'home', 'away', or 'draw'."""
    if home_score > away_score:
        return 'home'
    elif away_score > home_score:
        return 'away'
    else:
        return 'draw'

def calculate_match_score(prediction, actual):
    """Calculate score for a single match."""
    score = 0
    
    # Skip if actual result not available (999 indicates not played)
    if actual['home_score'] == 999 or actual['away_score'] == 999:
        return 0
    
    # Determine predicted and actual winners
    pred_winner = determine_winner(prediction['home_score'], prediction['away_score'])
    actual_winner = determine_winner(actual['home_score'], actual['away_score'])
    
    # 1 point for correct winner
    if pred_winner == actual_winner:
        score += 1
        
        # 2 extra points for correct score
        if prediction['home_score'] == actual['home_score'] and prediction['away_score'] == actual['away_score']:
            score += 2
    
    return score

def calculate_knockout_score(predicted_teams, actual_teams, points_per_team):
    """Calculate score for knockout stages."""
    score = 0
    if not predicted_teams or not actual_teams:
        return 0
    
    # Count correct teams
    correct_teams = set(predicted_teams) & set(actual_teams)
    score = len(correct_teams) * points_per_team
    
    return score

def calculate_final_winner_score(predicted_winner, actual_winner):
    """Calculate score for the final winner."""
    if predicted_winner and actual_winner and predicted_winner == actual_winner:
        return 64
    return 0

def calculate_person_score(prediction_data, actual_data):
    """Calculate total score for a person."""
    total_score = 0
    breakdown = {
        'group_stage': 0,
        'round_of_32': 0,
        'round_of_16': 0,
        'quarter_finals': 0,
        'semi_finals': 0,
        'finals_teams': 0,
        'finals_winner': 0,
        'total': 0
    }
    
    # Score group stage matches
    group_stage_score = 0
    for pred_match, actual_match in zip(prediction_data['matches'], actual_data['matches']):
        match_score = calculate_match_score(pred_match, actual_match)
        group_stage_score += match_score
    breakdown['group_stage'] = group_stage_score
    total_score += group_stage_score
    
    # Score Round of 32
    r32_score = calculate_knockout_score(
        prediction_data['round_of_32'],
        actual_data['round_of_32'],
        2
    )
    breakdown['round_of_32'] = r32_score
    total_score += r32_score
    
    # Score Round of 16
    r16_score = calculate_knockout_score(
        prediction_data['round_of_16'],
        actual_data['round_of_16'],
        4
    )
    breakdown['round_of_16'] = r16_score
    total_score += r16_score
    
    # Score Quarter Finals
    qf_score = calculate_knockout_score(
        prediction_data['quarter_finals'],
        actual_data['quarter_finals'],
        8
    )
    breakdown['quarter_finals'] = qf_score
    total_score += qf_score
    
    # Score Semi Finals
    sf_score = calculate_knockout_score(
        prediction_data['semi_finals'],
        actual_data['semi_finals'],
        16
    )
    breakdown['semi_finals'] = sf_score
    total_score += sf_score
    
    # Score Finals teams
    finals_teams_score = calculate_knockout_score(
        prediction_data['finals']['teams'],
        actual_data['finals']['teams'],
        32
    )
    breakdown['finals_teams'] = finals_teams_score
    total_score += finals_teams_score
    
    # Score Finals winner
    finals_winner_score = calculate_final_winner_score(
        prediction_data['finals']['winner'],
        actual_data['finals']['winner']
    )
    breakdown['finals_winner'] = finals_winner_score
    total_score += finals_winner_score
    
    breakdown['total'] = total_score
    
    return total_score, breakdown

# Main execution
if __name__ == '__main__':
    # Load data
    predictions = load_json('all_tournament_results.json')
    actual = load_json('current_results.json')
    
    print("=" * 70)
    print("WORLD CUP 2026 - TIPPING COMPETITION SCORES")
    print("=" * 70)
    
    # Calculate scores for each person
    scores = {}
    for person_name, person_prediction in predictions['predictions'].items():
        total_score, breakdown = calculate_person_score(person_prediction, actual['predictions']['results'])
        scores[person_name] = {
            'total': total_score,
            'breakdown': breakdown
        }
    
    # Display results sorted by score
    print("\nFINAL SCORES:")
    print("-" * 70)
    
    sorted_scores = sorted(scores.items(), key=lambda x: x[1]['total'], reverse=True)

    for rank, (person, data) in enumerate(sorted_scores, 1):
        print(f"\n{rank}. {person.upper():20} - {data['total']} points")
        print(f"   Group Stage:        {data['breakdown']['group_stage']:3} points")
        print(f"   Round of 32:        {data['breakdown']['round_of_32']:3} points")
        print(f"   Round of 16:        {data['breakdown']['round_of_16']:3} points")
        print(f"   Quarter Finals:     {data['breakdown']['quarter_finals']:3} points")
        print(f"   Semi Finals:        {data['breakdown']['semi_finals']:3} points")
        print(f"   Finals Teams:       {data['breakdown']['finals_teams']:3} points")
        print(f"   Finals Winner:      {data['breakdown']['finals_winner']:3} points")
    
    # Save scores to file
    with open('scores.json', 'w') as f:
        json.dump(scores, f, indent=2)
    
    print("\n" + "=" * 70)
    print("Scores saved to scores.json")
    print("=" * 70)
