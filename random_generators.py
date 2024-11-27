import random
import math

def geometric(p):
    """
    Generate a random number following geometric distribution.

    Args:
        p (float): Success probability parameter

    Returns:
        int: Random number following geometric distribution with parameter p
    """
    if p == 1:
        return 0
    rand = random.random()
    return math.floor(math.log(rand, 1-p))

def ModelGame(stats_home, stats_away):
    """
    Model game probabilities based on team statistics.

    Args:
        stats_home (dict): Statistics for home team
        stats_away (dict): Statistics for away team

    Returns:
        dict: Game probabilities containing:
            - home-team: Name of home team
            - away-team: Name of away team
            - wprob: Win probability
            - dprob: Draw probability
            - lprob: Loss probability
    """
    probabilities = {}
    probabilities['home-team'] = stats_home['name']
    probabilities['away-team'] = stats_away['name']
    home_power = stats_home['matches_won'] + stats_home['matches_home_won'] + stats_away['matches_lost'] + stats_away['matches_away_lost']
    away_power = stats_away['matches_won'] + stats_away['matches_away_won'] + stats_home['matches_lost'] + stats_home['matches_home_lost']
    draw_power = stats_home['matches_drawn'] + stats_home['matches_home_drawn'] + stats_away['matches_drawn'] + stats_away['matches_away_drawn']
    total_power = home_power + away_power + draw_power
    probabilities['wprob'] = home_power / total_power
    probabilities['dprob'] = draw_power / total_power
    probabilities['lprob'] = away_power / total_power
    return probabilities

def get_random_result(win_prob, draw_prob, loss_prob):
    """
    Generate a random match result based on given probabilities.

    Args:
        win_prob (float): Probability of home team winning
        draw_prob (float): Probability of draw
        loss_prob (float): Probability of away team winning

    Returns:
        str: Match result in format "home_score-away_score"
    """
    rand = random.random()
    if rand < win_prob:
        n = geometric(0.3)
        m = geometric(0.5) + n + 1
        return f"{m}-{n}"
    elif rand < win_prob + draw_prob:
        n = geometric(0.3)
        return f"{n}-{n}"
    else:
        n = geometric(0.3)
        m = geometric(0.5) + n + 1
        return f"{n}-{m}"
