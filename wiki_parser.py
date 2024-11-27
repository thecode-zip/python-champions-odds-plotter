import requests
from bs4 import BeautifulSoup

#This script fetches the matches of the champions league from wikipedia
#And writes them on a csv file called "wiki_matches.csv"

def fetch_champions_league_matches():
    """
    Fetch Champions League matches from Wikipedia and save them to a CSV file.

    Scrapes match data from the Wikipedia page for the current Champions League season
    and writes it to 'wiki_matches.csv' in the format:
    Sep=;
    score;home team;away team

    Raises:
        requests.RequestException: If there is an error fetching data from Wikipedia
    """
    url = "https://en.wikipedia.org/wiki/2024%E2%80%9325_UEFA_Champions_League_league_phase"
    
    try:
        # Send GET request to the website and raise exception if request fails
        response = requests.get(url)
        response.raise_for_status()
        
        # Open file for writing matches
        with open("wiki_matches.csv", "w", encoding='utf-8') as matches_file:
            matches_file.write("Sep=;\n")
            matches_file.write("score;home team;away team\n")
            matches_file.close()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all table elements with class="fevent"
        match_tables = soup.find_all('table', class_='fevent')
        for table in match_tables:

            #Get th class="fscore" element containing the score, if it exists
            score_element = table.find('th', class_='fscore')
            if score_element:
                score = score_element.contents[0]
            else:
                score = "N/A"
                
            # Find the team name spans
            team_names = table.find_all('span', attrs={'itemprop': 'name'})
            if len(team_names) >= 2:
                home_team = team_names[0].get_text(strip=True)
                away_team = team_names[1].get_text(strip=True)
                with open("wiki_matches.csv", "a", encoding='utf-8') as matches_file:
                    matches_file.write(f"{score};{home_team};{away_team}\n")
                    matches_file.close()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    fetch_champions_league_matches()
