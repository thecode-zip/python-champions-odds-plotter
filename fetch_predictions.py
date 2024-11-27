import requests
from bs4 import BeautifulSoup

#This script fetches the win probabilities from predicd.com
#And writes them on a csv file called "predicd_win_probabilities.csv"
#It exposes a function called fetch_predicd_win_probabilities for that effect

def fetch_predicd_win_probabilities():
    """
    Fetch match win probabilities from predicd.com and save them to a CSV file.

    Scrapes probability data for matches and writes them to 'predicd_odds.csv' in the format:
    Sep=;
    Date and Time;Home team;Away team;Pwin;Pdraw;Ploss

    Raises:
        requests.RequestException: If there is an error fetching data from predicd.com
    """
    url = "https://www.predicd.com/en/football/league/4480/"
    response = ""
    try:
        # Send GET request to the website
        response = requests.get(url)
        response.raise_for_status()
        
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return
    # Write the predictions to a file for debugging
    with open('predicd_odds.csv', 'w', encoding='utf-8') as f:
        f.write("Sep=;\n")
        f.write("Date and Time;Home team;Away team;Pwin;Pdraw;Ploss\n")
        f.close()

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    daily_games_span = soup.find_all('span', id="matchDayCarouselItem")
    date_match = ""
    for daily_games in daily_games_span:
        section = daily_games.find('section')
        if section:
            if int(section['matchday']) > 8 or int(section['matchday']) <= 0:
                continue
        
        table = daily_games.find('tbody')
        if not table:   
            continue
        
        for tr in table.find_all('tr'):
            #get day of match if tr element is one that contains a date
            day_match_element = daily_games.find('span', style="word-spacing: 100vw;")
            if day_match_element:
                date_match = day_match_element.text.strip()
            
            #Get the match info
            div1 = tr.find('div', class_='col-12 matchStats')
            divs_stats = tr.find_all('div', class_='col-xs-12 col-sm-6 matchStats')

            flag, mi = get_match_info(div1, divs_stats)
            if flag:
                with open('predicd_odds.csv', 'a', encoding='utf-8') as f:
                    f.write(f"{date_match};{mi['home_team']};{mi['away_team']};{mi['pwin']};{mi['pdraw']};{mi['ploss']}\n")
                    f.close()


def get_match_info(div1, divs_stats):
    """
    Extract match information from HTML elements.

    Args:
        div1 (BeautifulSoup element): HTML div containing match statistics
        divs_stats (list): List of HTML divs containing team statistics

    Returns:
        tuple: (success_flag, match_info_dict) where:
            - success_flag (bool): True if extraction was successful
            - match_info_dict (dict): Contains 'home_team', 'away_team', 'pwin', 'pdraw', 'ploss'
    """

    mi = {}
    
    if not div1 or len(divs_stats) < 2:
        return False, mi
    # Check home win probability
    match_table = div1.find('div', class_="progress-bar homeWin_Progressbar")
    if not match_table:
        return False, mi
    if 'aria-valuenow' not in match_table.attrs:
        return False, mi
    mi['pwin'] = match_table['aria-valuenow']

    # Check draw probability
    match_table = div1.find('div', class_="progress-bar draw_Progressbar")
    if not match_table:
        return False, mi
    if 'aria-valuenow' not in match_table.attrs:
        return False, mi
    mi['pdraw'] = match_table['aria-valuenow']
    
    # Check away win probability
    match_table = div1.find('div', class_="progress-bar awayWin_Progressbar")
    if not match_table:
        return False, mi
    if 'aria-valuenow' not in match_table.attrs:
        return False, mi
    mi['ploss'] = match_table['aria-valuenow']

    #the first div in divs_stats should contain the home team
    #the second div in divs_stats should contain the away teams
    div2 = divs_stats[0]
    div3 = divs_stats[1]

    # Check away win probability
    match_table = div2.find('h5', class_='card-title matchStatsCardTitle underline-home')
    if not match_table:
        return False, mi
    mi['home_team'] = match_table.text.strip()

    match_table = div3.find('h5', class_='card-title matchStatsCardTitle underline-away')
    if not match_table:
        return False, mi
    mi['away_team'] = match_table.text.strip()
    return True, mi


if __name__ == "__main__":
    fetch_predicd_win_probabilities()
