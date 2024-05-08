import requests
from bs4 import BeautifulSoup
import sqlite3

# Function to scrape Rivalry matches and extract relevant data
def scrape_hltv_matches():
    url = "https://www.rivalry.com/esports/csgo-betting"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        match_elements = soup.find_all('div', class_='betline m-auto betline-wide mb-0')
        matches_data = []
        for match in match_elements:
            team1_element = match.find('div', class_='outcome-name')
            odd1_element = match.find('div', class_='outcome-odds')
            hour_element = match.find('div', class_='text-navy dark:text-[#CFCFD1] leading-3 text-[11px]').text.strip()
            day = hour_element.split()
            month = f"{day[0]}"
            date = f"{day[1][:-4]}"
            hour = f"{day[1][-4:]} {day[2]}"

            if team1_element and odd1_element:
                team1 = team1_element.text.strip()
                odd1 = odd1_element.text.strip()

                team2_element = team1_element.find_next('div', class_='outcome-name')
                odd2_element = odd1_element.find_next('div', class_='outcome-odds')

                if team2_element and odd2_element:
                    team2 = team2_element.text.strip()
                    odd2 = odd2_element.text.strip() 

                    matches_data.append({'team1': team1, 'odd1': odd1, 'team2': team2, 'odd2': odd2, 'month': month, 'date': date, 'hour': hour})
                return matches_data
    else:
        print("Error: Failed to retrieve data from HLTV")
        return None

# Function to load and save data into a DataFrame
def load_save_data(matches_data):
    if matches_data:
        db_file = '/airflow/storage/bronze_db/bet_matches.db'
        try:
            conn = sqlite3.connect(db_file)
            # Create a cursor object to execute SQL queries
            cursor = conn.cursor()
            # Define the table name based on the current date
            table_name = "matches_rivalry"
            # Create a table to store match details
            cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} (team1 TEXT, odd1 REAL, odd2 REAL, team2 TEXT, month TEXT, date REAL, hour TEXT)')
            # Insert match details into the table
            for match in matches_data:
                cursor.execute(f'INSERT INTO {table_name} (team1, odd1, odd2, team2, month, date, hour) VALUES (?, ?, ?, ?, ?, ?, ?)', (match['team1'], match['odd1'], match['odd2'], match['team2'], match['month'], match['date'], match['hour']))
            # Commit the transaction
            conn.commit()
            print(f"Data successfully loaded into table '{table_name}' in {db_file}")
            # sqlite3 /airflow/storage/bet_matches.db
        except sqlite3.Error as e:
            print("SQLite error:", e)
        finally:
            conn.close()
    else:
        print("No data to load")

if __name__ == "__main__":
    # Extract data from HLTV matches webpage
    matches_data = scrape_hltv_matches()
    # Load data into DataFrame and save to DB
    load_save_data(matches_data)
