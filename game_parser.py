#This script parses the file wiki_matches.txt and creates a new file called wiki_matches_parsed.xml and stats.xml

from statistics_and_rankings import MakeStatistics, MakeRanking
from fetch_predictions import fetch_predicd_win_probabilities
from wiki_parser import fetch_champions_league_matches
from random_generators import ModelGame, get_random_result

import csv
import time
from difflib import SequenceMatcher
import matplotlib.pyplot as plt
import numpy as np
import random
import os

def string_similarity(a, b):
    """
    Calculate similarity ratio between two strings.

    Args:
        a (str): First string
        b (str): Second string

    Returns:
        float: Similarity ratio between 0 and 1
    """
    return SequenceMatcher(None, a, b).ratio()

def parse_wiki_matches():
    """
    Parse matches from wiki_matches.csv file.

    Returns:
        tuple: (matches_list, matches_to_generate, set_teams_from_wiki) where:
            - matches_list: List of completed matches with scores
            - matches_to_generate: List of future matches without scores
            - set_teams_from_wiki: Set of all team names from Wikipedia
    """
    matches_list = []
    matches_to_generate = []
    set_teams_from_wiki = set()

    #parse wiki_matches.csv
    with open("wiki_matches.csv", "r", encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        next(reader) # skip delimiter line
        next(reader) # Skip header
        for row in reader:
            set_teams_from_wiki.add(row[1])
            set_teams_from_wiki.add(row[2])
            if row[0] == "v":
                matches_to_generate.append((row[1], row[2]))
            else:
                matches_list.append([row[1], row[2]] + [int(a) for a in row[0].split('–')])

    return matches_list, matches_to_generate, set_teams_from_wiki

def parse_predicd_odds():
    """
    Parse match odds from predicd_odds.csv file.

    Returns:
        tuple: (match_prediction_from_predicd, set_teams_from_predicd) where:
            - match_prediction_from_predicd: List of match predictions with probabilities
            - set_teams_from_predicd: Set of all team names from Predicd
    """
    set_teams_from_predicd = set()
    match_predition_from_predicd = []
    with open("predicd_odds.csv", "r", encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        next(reader) # skip delimiter line
        next(reader) # Skip header
        for row in reader:
            set_teams_from_predicd.add(row[1])
            set_teams_from_predicd.add(row[2])
            match_predition_from_predicd.append({'home-team': row[1], 
                                            'away-team': row[2], 
                                            'wprob': float(row[3])/100, 
                                            'dprob': float(row[4])/100, 
                                            'lprob': float(row[5])/100})
    return match_predition_from_predicd, set_teams_from_predicd

def get_ranks(matches_list):
    """
    Generate rankings from a list of matches.

    Args:
        matches_list (list): List of matches with scores

    Returns:
        list: Ranked list of teams based on performance
    """
    stats = MakeStatistics(matches_list)
    ranks = MakeRanking(stats)
    return ranks

def print_ranks(ranks):
    """
    Print team rankings in a formatted way.

    Args:
        ranks (list): List of team rankings to display
    """
    for index, rank in enumerate(ranks):
        print(f"pos = {1 + index} :: {rank['name']}, pt: {rank['points']}, gd: {rank['goals_difference']}, gf: {rank['goals_for']}, ga: {rank['goals_for_away']}")

def correct_missmatched_names(set_teams_from_wiki, set_teams_from_predicd):
    """
    Match team names between Wikipedia and Predicd data using string similarity.

    Args:
        set_teams_from_wiki (set): Set of team names from Wikipedia
        set_teams_from_predicd (set): Set of team names from Predicd

    Returns:
        dict: Mapping of Predicd team names to Wikipedia team names
    """
    #Generate a missmatch matrix
    missmatch_score = {}
    for team_wiki in set_teams_from_wiki:
        missmatch_score[team_wiki] = {}
        for team_predicd in set_teams_from_predicd:
            missmatch_score[team_wiki][team_predicd] = string_similarity(team_wiki, team_predicd)
    match_predicd_to_wiki = {}
    
    #Find lexicographically best matching using a greedy algorithm
    while len(missmatch_score) > 0:
        max_key_wiki, max_key_predicd, max_score = "", "", 0
        for team_wiki in missmatch_score:
            for team_predicd in missmatch_score[team_wiki]:
                if missmatch_score[team_wiki][team_predicd] > max_score:
                    max_score = missmatch_score[team_wiki][team_predicd]
                    max_key_wiki = team_wiki
                    max_key_predicd = team_predicd
        match_predicd_to_wiki[max_key_predicd] = max_key_wiki
        del missmatch_score[max_key_wiki]
        for team_wiki in missmatch_score:
            del missmatch_score[team_wiki][max_key_predicd]
            if len(missmatch_score[team_wiki]) == 0:
                del missmatch_score[team_wiki]
    
    return match_predicd_to_wiki

def missing_matches(matches_to_generate, match_predition_from_predicd, team_stats):
    """
    Generate predictions for matches missing from Predicd data.

    Args:
        matches_to_generate (list): List of matches needing predictions
        match_predition_from_predicd (list): List of existing match predictions

    Returns:
        list: Complete list of match predictions including generated ones
    """
    matches_to_generate_predicd = []
    for game in matches_to_generate:
        game_found = False
        for probabilities in match_predition_from_predicd:
            if probabilities['home-team'] == game[0] and probabilities['away-team'] == game[1]:
                matches_to_generate_predicd.append(probabilities)
                game_found = True
                break
        if not game_found:
            probabilities = ModelGame(team_stats[game[0]], team_stats[game[1]])
            matches_to_generate_predicd.append(probabilities)
    return matches_to_generate_predicd

def create_matches_list(print_current_stats=False):
    """
    Create a complete list of matches combining Wikipedia and Predicd data.

    Args:
        print_current_stats (bool): Whether to print current statistics

    Returns:
        tuple: (matches_list, matches_to_generate_predicd) where:
            - matches_list: List of completed matches
            - matches_to_generate_predicd: List of future matches with predictions
    """
    #parse wiki file
    matches_list, matches_to_generate, set_teams_from_wiki = parse_wiki_matches()
    stats = MakeStatistics(matches_list)

    if print_current_stats:
        ranks = MakeRanking(stats)
        print_ranks(ranks)
    
    #parse predicd file
    match_predition_from_predicd, set_teams_from_predicd = parse_predicd_odds()

    #deal with name missmatch
    match_predicd_to_wiki = correct_missmatched_names(set_teams_from_wiki, set_teams_from_predicd)
    for game in match_predition_from_predicd:
        game['home-team'] = match_predicd_to_wiki[game['home-team']]
        game['away-team'] = match_predicd_to_wiki[game['away-team']]

    #get missing matches
    matches_to_generate_predicd = missing_matches(matches_to_generate, match_predition_from_predicd, stats)

    return matches_list, matches_to_generate_predicd

def create_rank_statistics(results_list):
    stats_tracked = {}
    ranks = get_ranks(results_list)
    for index, rank in enumerate(ranks):
        stats_tracked[rank['name'] + "_points"] = rank['points']
        stats_tracked[rank['name'] + "_goaldifference"] = rank['goals_difference']
        stats_tracked[rank['name'] + "_position"] = index + 1
    for i in range(1, len(ranks)+1):
        stats_tracked[str(i) + "_position_points"] = ranks[i-1]['points']
        stats_tracked[str(i) + "_position_goaldifference"] = ranks[i-1]['goals_difference']
    return stats_tracked

def write_stats_to_file(statistics_to_track):
    """
    Write statistics to a CSV file.
    """
    with open("statistics.csv", "w", encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(statistics_to_track[0].keys())
        for stat in statistics_to_track:
            writer.writerow(stat.values())
    return

def save_plot_pictures(statistics_to_track):
    """
    Save plot pictures of statistics using matplotlib.
    """

    #get list of classifications
    
    teams = [key.split('_')[0] for key in statistics_to_track[0].keys() if key.endswith('_position')]
    classifications = set()
    for team in teams:
        for stat in statistics_to_track:
            classifications.add(stat[f'{team}_position'])
    classifications = sorted(list(classifications))
    
    plot_position_distribution(statistics_to_track, classifications, teams)
    plot_8th_and_24th_position_distribution(statistics_to_track)
    plot_probability_first_position(statistics_to_track, teams)
    plot_probability_last_position(statistics_to_track, teams)
    return

def plot_probability_first_position(statistics_to_track, teams):
    # Create figure and axis
    plt.figure(figsize=(12, 8))
    positions = {team: [stat[f'{team}_position'] for stat in statistics_to_track] for team in teams}
    position_distributions = {team:positions[team].count(1)/len(positions[team]) for team in teams}
    # Create bar chart
    plt.bar(position_distributions.keys(), position_distributions.values())
    
    # Customize the plot
    plt.title('Probability of Teams Finishing in First Position')
    plt.xlabel('Teams')
    plt.ylabel('Probability')
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('first_position_probability.png', bbox_inches='tight', dpi=900)
    plt.close()
    return

def plot_probability_last_position(statistics_to_track, teams):
    # Create figure and axis
    plt.figure(figsize=(12, 8))
    positions = {team: [stat[f'{team}_position'] for stat in statistics_to_track] for team in teams}
    position_distributions = {team:positions[team].count(36)/len(positions[team]) for team in teams}
    # Create bar chart
    plt.bar(position_distributions.keys(), position_distributions.values())
    
    # Customize the plot
    plt.title('Probability of Teams Finishing in Last Position')
    plt.xlabel('Teams')
    plt.ylabel('Probability')
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('last_position_probability.png', bbox_inches='tight', dpi=900)
    plt.close()
    return

def plot_position_distribution(statistics_to_track, classifications, all_teams):
    # Create figure and axis
    plt.figure(figsize=(12, 8))

    teams = random.sample(all_teams, 8)
    positions = {team: [stat[f'{team}_position'] for stat in statistics_to_track] for team in teams}
    position_distributions = {team:[positions[team].count(i)/len(positions[team]) for i in classifications] for team in teams}
    

    x = np.arange(len(classifications))  # the label locations
    width = 1/(len(teams) + 1)  # the width of the bars
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained')

    for attribute, measurement in position_distributions.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
        #ax.bar_label(rects, padding=3)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Probability')
    ax.set_xlabel('Classification', fontsize=8)
    ax.set_title('Classification of teams in champions league\n Distribution of classification of teams over Monte Carlo trials', fontsize=10, y=1.05)
    ax.set_xticks(x + width, classifications, fontsize=4)
    ax.legend(loc='upper left', ncols=4, fontsize=7)
    ax.set_ylim(0, 1)

    # Add vertical lines at 8.5 and 24.5
    ax.axvline(x=8.5, color='black', linestyle='-', linewidth=1)
    ax.axvline(x=24.5, color='black', linestyle='-', linewidth=1)
    
    # Save the bar plot
    plt.savefig('position_distribution.png', bbox_inches='tight', dpi=900)
    plt.close()
    return

def plot_8th_and_24th_position_distribution(statistics_to_track):
    # Create figure and axis
    plt.figure(figsize=(12, 8))
    
    max_points = max([stat['8_position_points'] for stat in statistics_to_track])
    min_points = min([stat['24_position_points'] for stat in statistics_to_track])

    position_distributions = {"8th position points": [[stat['8_position_points'] for stat in statistics_to_track].count(i)/len(statistics_to_track) for i in range(min_points, max_points + 1)],
                             "24th position points": [[stat['24_position_points'] for stat in statistics_to_track].count(i)/len(statistics_to_track) for i in range(min_points, max_points + 1)]}

    x = np.arange(min_points, max_points+1)  # the label locations
    width = 1/(2 + 1)  # the width of the bars
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained')
    for attribute, measurement in position_distributions.items():
        offset = width * multiplier
        rects = ax.bar([a + offset for a in x], measurement, width, label=attribute)
        #ax.bar_label(rects, padding=3)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Probability')
    ax.set_xlabel('Number of points of team at given position', fontsize=12)
    ax.set_title('Distribution of number of points of teams at 8th and 24th position over Monte Carlo trials', fontsize=10, y=1.05)
    ax.set_xticks(x + width, x, fontsize=10)
    ax.legend(loc='upper left')
    ax.set_ylim(0, 1)
    
    # Save the bar plot
    plt.savefig('8th_and_24th_position_distribution.png', bbox_inches='tight', dpi=900)
    plt.close()
    return

if __name__ == "__main__":
    begin_time = time.time()
    generateNewMatches = False
    if generateNewMatches or not os.path.isfile("wiki_matches.csv"):
        fetch_champions_league_matches()
    if generateNewMatches or not os.path.isfile("predicd_odds.csv"):
        fetch_predicd_win_probabilities()
    matches_list, matches_to_generate_predicd = create_matches_list()
    
    statistics_to_track = []
    TRIAL_NUMBER = 10000
    
    for trial_number in range(TRIAL_NUMBER):
        new_results = []
        for game in matches_to_generate_predicd:
            result = get_random_result(game['wprob'], game['dprob'], game['lprob'])
            new_results.append([game['home-team'], game['away-team']] + [int(a) for a in result.split('-')])
        stats_tracked = create_rank_statistics(matches_list + new_results)
        stats_tracked["trial_number"] = trial_number + 1
        statistics_to_track.append(stats_tracked)

    #Save statistics to file
    write_stats_to_file(statistics_to_track)
    
    #create and save plot pictures
    save_plot_pictures(statistics_to_track)
    
    end_time = time.time()
    print("Time elapsed: ", round(end_time - begin_time, 3), "seconds")

