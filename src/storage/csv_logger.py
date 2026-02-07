import csv
import os
import config


def ensure_csv_header():
    """Write CSV header only if file doesn't exist."""
    if not os.path.exists(config.OUTPUT_CSV):
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(config.OUTPUT_CSV), exist_ok=True)
        
        with open(config.OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                "Timestamp", "MatchID", "Player1", "Player2", 
                "P1 Ranking", "P2 Ranking",
                "Tournament", "SetsScore", "GamesScore", "CurrentSetGames",
                "P1 1stServe%", "P2 1stServe%", 
                "P1 2ndServePts%", "P2 2ndServePts%", 
                "P1 OppPtsOnServe", "P2 OppPtsOnServe", 
                "P1 BPFaced", "P2 BPFaced", 
                "P1 BPSaved", "P2 BPSaved",
                "P1 Aces", "P2 Aces",
                "P1 DoubleFaults", "P2 DoubleFaults",
                "P1 TotalPoints", "P2 TotalPoints",
                "P1 ServicePointsWon", "P2 ServicePointsWon",
                "P1 ReceiverPointsWon", "P2 ReceiverPointsWon",
                "P1 GamesWon", "P2 GamesWon",
                "P1 FirstServePoints", "P2 FirstServePoints",
                "P1 SecondServePoints", "P2 SecondServePoints",
                "P1 BPConverted", "P2 BPConverted",
                "StartingOdds", "LiveOdds"
            ])


def log_match_to_csv(match_data, stats_dict, starting_odds, odds_str):
    """Log match data to CSV file."""
    with open(config.OUTPUT_CSV, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        current_set_games_str = f"{match_data['current_set_games_home']}-{match_data['current_set_games_away']}" if match_data['current_set_games_home'] is not None and match_data['current_set_games_away'] is not None else "N/A"
        
        writer.writerow([
            match_data['timestamp'],
            match_data['match_id'],
            match_data['player1'],
            match_data['player2'],
            match_data['p1_ranking'] or "N/A",
            match_data['p2_ranking'] or "N/A",
            match_data['tour_type'],
            match_data['sets_score'],
            match_data['games_score'],
            current_set_games_str,
            stats_dict['p1_first_serve_pct'], stats_dict['p2_first_serve_pct'],
            stats_dict['p1_second_serve_pts_pct'], stats_dict['p2_second_serve_pts_pct'],
            stats_dict['p1_opp_pts_on_serve'], stats_dict['p2_opp_pts_on_serve'],
            stats_dict['p1_bp_faced'], stats_dict['p2_bp_faced'],
            stats_dict['p1_bp_saved'], stats_dict['p2_bp_saved'],
            stats_dict['p1_aces'], stats_dict['p2_aces'],
            stats_dict['p1_double_faults'], stats_dict['p2_double_faults'],
            stats_dict['p1_total_points'], stats_dict['p2_total_points'],
            stats_dict['p1_service_points_won'], stats_dict['p2_service_points_won'],
            stats_dict['p1_receiver_points_won'], stats_dict['p2_receiver_points_won'],
            stats_dict['p1_games_won'], stats_dict['p2_games_won'],
            stats_dict['p1_first_serve_points'], stats_dict['p2_first_serve_points'],
            stats_dict['p1_second_serve_points'], stats_dict['p2_second_serve_points'],
            stats_dict['p1_bp_converted'], stats_dict['p2_bp_converted'],
            starting_odds,
            odds_str
        ])

