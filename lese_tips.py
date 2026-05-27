import pandas as pd
import json
import glob
from datetime import datetime
from pathlib import Path

def extract_tournament_data(excel_file):
    """
    Extract all tournament data from an Excel file.
    Returns a dictionary containing all matches and tournament stages.
    """
    df = pd.read_excel(excel_file, sheet_name='2026 World Cup', header=None)
    
    tournament_data = {
        'file': excel_file,
        'extraction_date': datetime.now().isoformat(),
        'matches': [],
        'round_of_32': [],
        'round_of_16': [],
        'quarter_finals': [],
        'semi_finals': [],
        'finals': {
            'teams': [],
            'scores': [],
            'winner': None,
            'winner_score': None
        }
    }
    
    # Extract Group Stage Matches (rows 7-78, columns E-H)
    for idx in range(6, 78):
        match = {
            'home': df.iloc[idx, 4],
            'home_score': int(df.iloc[idx, 5]) if pd.notna(df.iloc[idx, 5]) else None,
            'away_score': int(df.iloc[idx, 6]) if pd.notna(df.iloc[idx, 6]) else None,
            'away': df.iloc[idx, 7]
        }
        tournament_data['matches'].append(match)
    
    # Extract Round of 32 (column BL - index 63)
    row_indices_r32 = [9, 10, 13, 14, 17, 18, 21, 22, 25, 26, 29, 30, 33, 34, 37, 38, 41, 42, 45, 46, 49, 50, 53, 54, 57, 58, 61, 62, 65, 66, 69, 70]
    for idx in row_indices_r32:
        team = df.iloc[idx, 63]
        if pd.notna(team):
            tournament_data['round_of_32'].append(team)
    
    # Extract Round of 16 (column BS - index 70)
    row_indices_r16 = [11, 12, 19, 20, 27, 28, 35, 36, 43, 44, 51, 52, 59, 60, 67, 68]
    for idx in row_indices_r16:
        team = df.iloc[idx, 70]
        if pd.notna(team):
            tournament_data['round_of_16'].append(team)
    
    # Extract Quarter Finals (column BZ - index 77)
    row_indices_qf = [15, 16, 31, 32, 47, 48, 63, 64]
    for idx in row_indices_qf:
        team = df.iloc[idx, 77]
        if pd.notna(team):
            tournament_data['quarter_finals'].append(team)
    
    # Extract Semi Finals (column CG - index 84)
    row_indices_sf = [22, 23, 54, 55]
    for idx in row_indices_sf:
        team = df.iloc[idx, 84]
        if pd.notna(team):
            tournament_data['semi_finals'].append(team)
    
    # Extract Finals (column CN - index 91, CO - index 92)
    row_indices_finals = [36, 37]
    for idx in row_indices_finals:
        team = df.iloc[idx, 91]
        score = df.iloc[idx, 92]
        if pd.notna(team):
            tournament_data['finals']['teams'].append(team)
            tournament_data['finals']['scores'].append(int(score) if pd.notna(score) else None)
    
    # Determine Finals Winner
    if len(tournament_data['finals']['teams']) == 2:
        scores = tournament_data['finals']['scores']
        if all(s is not None for s in scores):
            if scores[0] > scores[1]:
                tournament_data['finals']['winner'] = tournament_data['finals']['teams'][0]
                tournament_data['finals']['winner_score'] = scores[0]
            else:
                tournament_data['finals']['winner'] = tournament_data['finals']['teams'][1]
                tournament_data['finals']['winner_score'] = scores[1]
    
    return tournament_data

def save_results(tournament_data, output_file='tournament_results.json'):
    """Save tournament data to JSON file."""
    with open(output_file, 'w') as f:
        json.dump(tournament_data, f, indent=2)
    print(f"Results saved to {output_file}")

def display_results(tournament_data):
    """Display tournament data in a formatted way."""
    print("=" * 60)
    print("WORLD CUP 2026 - TOURNAMENT RESULTS")
    print("=" * 60)
    
    # Group Stage Matches
    print(f"\nGROUP STAGE MATCHES ({len(tournament_data['matches'])}):")
    print("-" * 60)
    for i, match in enumerate(tournament_data['matches'], 1):
        home = match['home']
        away = match['away']
        home_score = match['home_score'] if match['home_score'] is not None else '-'
        away_score = match['away_score'] if match['away_score'] is not None else '-'
        print(f"{i:2d}. {home} {home_score} - {away_score} {away}")
    
    # Round of 32
    print(f"\nROUND OF 32 ({len(tournament_data['round_of_32'])}):")
    print("-" * 60)
    for i, team in enumerate(tournament_data['round_of_32'], 1):
        print(f"{i:2d}. {team}")
    
    # Round of 16
    print(f"\nROUND OF 16 ({len(tournament_data['round_of_16'])}):")
    print("-" * 60)
    for i, team in enumerate(tournament_data['round_of_16'], 1):
        print(f"{i:2d}. {team}")
    
    # Quarter Finals
    print(f"\nQUARTER FINALS ({len(tournament_data['quarter_finals'])}):")
    print("-" * 60)
    for i, team in enumerate(tournament_data['quarter_finals'], 1):
        print(f"{i:2d}. {team}")
    
    # Semi Finals
    print(f"\nSEMI FINALS ({len(tournament_data['semi_finals'])}):")
    print("-" * 60)
    for i, team in enumerate(tournament_data['semi_finals'], 1):
        print(f"{i:2d}. {team}")
    
    # Finals
    print(f"\nFINALS:")
    print("-" * 60)
    finals = tournament_data['finals']
    for i, team in enumerate(finals['teams'], 1):
        score = finals['scores'][i-1] if i <= len(finals['scores']) else '-'
        print(f"{i}. {team} - Score: {score}")
    
    # Winner
    if finals['winner']:
        print("\n" + "=" * 60)
        print(f"WORLD CUP CHAMPION 2026: {finals['winner']} ({finals['winner_score']})")
        print("=" * 60)

# Main execution
if __name__ == '__main__':
    # Find all Excel files in the current directory
    excel_files = glob.glob('*.xlsx')
    
    if not excel_files:
        print("No Excel files found in the current directory.")
        exit(1)
    
    print(f"Found {len(excel_files)} Excel file(s): {', '.join(excel_files)}\n")
    
    # Store all results
    all_results = {
        'extraction_date': datetime.now().isoformat(),
        'files_processed': len(excel_files),
        'predictions': {}
    }
    
    # Process each Excel file
    for excel_file in sorted(excel_files):
        try:
            print(f"\n{'='*70}")
            print(f"PROCESSING: {excel_file}")
            print('='*70)
            
            results = extract_tournament_data(excel_file)
            display_results(results)
            
            # Store results in the combined dictionary
            file_name = Path(excel_file).stem  # Get filename without extension
            all_results['predictions'][file_name] = results
            
        except Exception as e:
            print(f"Error processing {excel_file}: {e}")
            continue
    
    # Save all results to a combined JSON file
    print(f"\n{'='*70}")
    print("SAVING ALL RESULTS")
    print('='*70)
    save_results(all_results, 'all_tournament_tips.json')
    print("\nAll predictions saved to all_tournament_tips.json")
    
    # Print summary comparison
    print(f"\n{'='*70}")
    print("COMPARISON SUMMARY")
    print('='*70)
    for person, data in all_results['predictions'].items():
        winner = data['finals']['winner'] if data['finals']['winner'] else "Unknown"
        score = data['finals']['winner_score'] if data['finals']['winner_score'] else "N/A"
        print(f"{person:20} -> {winner} ({score})")

