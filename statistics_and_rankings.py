#This file contains two methods that parse a list of matches and give stats and rankings, as long as the matches are correctly formatted

def MakeStatistics(matches):
    """
    Generate statistics from a list of matches.

    Args:
        matches (list): List of matches where each match is [hometeam, awayteam, hometeam_score, awayteam_score]

    Returns:
        dict: Dictionary containing statistics for each team with the following keys:
            - matches_played, matches_won, matches_drawn, matches_lost, points
            - goals_for, goals_against, goals_difference
            - matches_home_played, matches_home_won, matches_home_drawn, matches_home_lost
            - goals_for_home, goals_against_home, goals_difference_home
            - matches_away_played, matches_away_won, matches_away_drawn, matches_away_lost
            - goals_for_away, goals_against_away, goals_difference_away
            - league_opponents, league_opponents_points, league_opponents_goal_difference, league_opponents_goals_for
    """
    #This function makes statistics from a list of matches = [match1, match2, ... ]
    #The match structure is the following:
    #match = [ hometeam, awayteam, hometeam_score, awayteam_score ]
    #The output is a dictionary for each team, identified by its name as a string, and returns a dictionary with the following keys:
    #'matches_played', 'matches_won', 'matches_drawn', 'matches_lost', 'points'
    #'goals_for', 'goals_against', 'goals_difference'
    #'matches_home_played', 'matches_home_won', 'matches_home_drawn', 'matches_home_lost', 
    #'goals_for_home', 'goals_against_home', 'goals_difference_home'
    #'matches_away_played', 'matches_away_won', 'matches_away_drawn', 'matches_away_lost', 
    #'goals_for_away', 'goals_against_away', 'goals_difference_away'
    #'league_opponents', 'league_opponents_points', 'league_opponents_goal_difference', 'league_opponents_goals_for'

    teams = {}
    for home_team, away_team, home_score, away_score in matches:
        if home_team not in teams:
            teams[home_team] = {
                'name': home_team,
                'matches_played': 0, 'matches_won': 0, 'matches_drawn': 0, 'matches_lost': 0, 'points': 0, 
                'goals_for': 0, 'goals_against': 0, 'goals_difference': 0,
                'matches_home_played': 0, 'matches_home_won': 0, 'matches_home_drawn': 0, 'matches_home_lost': 0, 
                'goals_for_home': 0, 'goals_against_home': 0, 'goals_difference_home': 0,
                'matches_away_played': 0, 'matches_away_won': 0, 'matches_away_drawn': 0, 'matches_away_lost': 0,
                'goals_for_away': 0, 'goals_against_away': 0, 'goals_difference_away': 0,
                'league_opponents': []
            }
        if away_team not in teams:
            teams[away_team] = {
                'name': away_team,
                'matches_played': 0, 'matches_won': 0, 'matches_drawn': 0, 'matches_lost': 0, 'points': 0, 
                'goals_for': 0, 'goals_against': 0, 'goals_difference': 0,
                'matches_home_played': 0, 'matches_home_won': 0, 'matches_home_drawn': 0, 'matches_home_lost': 0, 
                'goals_for_home': 0, 'goals_against_home': 0, 'goals_difference_home': 0,
                'matches_away_played': 0, 'matches_away_won': 0, 'matches_away_drawn': 0, 'matches_away_lost': 0,
                'goals_for_away': 0, 'goals_against_away': 0, 'goals_difference_away': 0,
                'league_opponents': []
            }

    for home_team, away_team, home_score, away_score in matches:
        home_team_stats = teams[home_team]
        away_team_stats = teams[away_team]

        home_team_stats['matches_played'] += 1
        away_team_stats['matches_played'] += 1

        home_team_stats['matches_home_played'] += 1
        away_team_stats['matches_away_played'] += 1

        home_team_stats['goals_for'] += home_score
        home_team_stats['goals_for_home'] += home_score
        away_team_stats['goals_for'] += away_score
        away_team_stats['goals_for_away'] += away_score
        home_team_stats['goals_against'] += away_score
        home_team_stats['goals_against_home'] += away_score
        away_team_stats['goals_against'] += home_score
        away_team_stats['goals_against_away'] += home_score
        home_team_stats['goals_difference'] += home_score - away_score
        home_team_stats['goals_difference_home'] += home_score - away_score
        away_team_stats['goals_difference'] += away_score - home_score
        away_team_stats['goals_difference_away'] += away_score - home_score

        home_team_stats['league_opponents'].append(away_team)
        away_team_stats['league_opponents'].append(home_team)

        if home_score > away_score:
            home_team_stats['matches_won'] += 1
            away_team_stats['matches_lost'] += 1
            home_team_stats['points'] += 3
            home_team_stats['matches_home_won'] += 1
            away_team_stats['matches_away_lost'] += 1
        elif home_score < away_score:
            away_team_stats['matches_won'] += 1
            home_team_stats['matches_lost'] += 1
            away_team_stats['points'] += 3
            away_team_stats['matches_away_won'] += 1
            home_team_stats['matches_home_lost'] += 1
        else:
            home_team_stats['matches_drawn'] += 1
            away_team_stats['matches_drawn'] += 1
            home_team_stats['points'] += 1
            away_team_stats['points'] += 1
            home_team_stats['matches_home_drawn'] += 1
            away_team_stats['matches_away_drawn'] += 1

    for team_stats in teams.values():
        team_stats['league_opponents_points'] = sum([teams[opponent]['points'] for opponent in team_stats['league_opponents']])
        team_stats['league_opponents_goal_difference'] = sum([teams[opponent]['goals_difference'] for opponent in team_stats['league_opponents']])
        team_stats['league_opponents_goals_for'] = sum([teams[opponent]['goals_for'] for opponent in team_stats['league_opponents']])

    return teams

def MakeRanking(statistics):
    """
    Generate rankings from team statistics.

    Args:
        statistics (dict): Dictionary containing team statistics as generated by MakeStatistics()

    Returns:
        list: Sorted list of teams ranked by:
            1. Points
            2. Goal difference
            3. Goals scored
            4. Away goals
            5. Matches won
            6. Away matches won
            7. League opponents points
            8. League opponents goal difference
            9. League opponents goals scored
            10. Team name (alphabetically)
    """
    #This function makes a ranking from a list of statistics statistics = {team1: stats1, team2: stats2, ... }
    #each statistic is a dictionary with the following keys:
    #'matches_played', 'matches_won', 'matches_drawn', 'matches_lost', 'points'
    #'goals_for', 'goals_against', 'goals_difference'
    #'matches_home_played', 'matches_home_won', 'matches_home_drawn', 'matches_home_lost', 
    #'goals_for_home', 'goals_against_home', 'goals_difference_home'
    #'matches_away_played', 'matches_away_won', 'matches_away_drawn', 'matches_away_lost', 
    #'goals_for_away', 'goals_against_away', 'goals_difference_away'
    #'league_opponents_points', 'league_opponents_goal_difference', 'league_opponents_goals_for'
    ranking = [value for value in statistics.values()] 
    ranking.sort(key=lambda x: (-x['points'], 
                                                        -x['goals_difference'], 
                                                        -x['goals_for'], 
                                                        -x['goals_for_away'], 
                                                        -x['matches_won'], 
                                                        -x['matches_away_won'], 
                                                        -x['league_opponents_points'], 
                                                        -x['league_opponents_goal_difference'], 
                                                        -x['league_opponents_goals_for'], 
                                                        x['name']))#In case of a tie, sort alphabetically, I'm not paid enough to do better
    return ranking
