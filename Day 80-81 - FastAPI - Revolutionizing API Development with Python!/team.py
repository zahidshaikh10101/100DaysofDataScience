from bs4 import BeautifulSoup
import requests
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/team-info")
def info_model(team: str):
    # Validate the team input
    if not team or not isinstance(team, str):
        raise HTTPException(status_code=400, detail="Invalid team name provided.")

    team = team.upper()

    # Prepare team name for URL
    team_mapping = {
        'MI': 'Mumbai Indians', 'MUMBAI': 'Mumbai Indians',
        'CSK': 'Chennai Super Kings', 'CHENNAI': 'Chennai Super Kings',
        'RCB': 'Royal Challengers Banglore', 'BANGALORE': 'Royal Challengers Banglore',
        'KKR': 'Kolkata Knight Riders', 'KOLKATA': 'Kolkata Knight Riders',
        'DC': 'Delhi Capitals', 'DELHI': 'Delhi Capitals',
        'PK': 'Punjab Kings', 'PUNJAB': 'Punjab Kings',
        'LSG': 'Lucknow Super Giants', 'LUCKNOW': 'Lucknow Super Giants',
        'SRH': 'Sunrisers Hyderabad', 'HYDERABAD': 'Sunrisers Hyderabad',
        'RR': 'Rajasthan Royals', 'RAJASTHAN': 'Rajasthan Royals',
        'GT': 'Gujarat Titans', 'GUJARAT': 'Gujarat Titans'
    }
    team = team_mapping.get(team, team).replace(' ', '-').lower()
    base_url = f"https://www.iplt20.com/teams/{team}"

    # Fetch the webpage
    try:
        response = requests.get(base_url)
        response.raise_for_status()  # Raise an HTTP error for bad status codes
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data from IPL website: {e}")

    soup = BeautifulSoup(response.text, "html.parser")

    # Initialize dictionaries
    team_data = {}
    roles_dict = {'Batter': [], 'Bowler': [], 'All-rounder': []}

    # Extract team name
    team_name_div = soup.find("div", class_="vn-teamTitleODet")
    if team_name_div:
        name_h2 = team_name_div.find("h2")
        if name_h2:
            team_data["team name"] = name_h2.get_text(strip=True)

    # Extract team website
    website_urls = soup.find_all("a", class_="vn-button")
    for tag in website_urls:
        if 'href' in tag.attrs:
            team_data["team website"] = tag['href']
            break

    # Extract team logo
    logo_div = soup.find("div", class_="vn-teamBanLogo team-sm-lg")
    if logo_div:
        img_tag = logo_div.find("img")
        if img_tag and 'src' in img_tag.attrs:
            team_data["logo"] = img_tag['src']

    # Extract owner, coach, venue, captain details
    details_div = soup.find("div", class_="team-detail-text")
    if details_div:
        details = details_div.find_all("p")
        for detail in details:
            text = detail.get_text(strip=True)
            if "Owner" in text:
                team_data["owner"] = text.split("-")[-1].strip()
            elif "Coach" in text:
                team_data["coach"] = text.split("-")[-1].strip()
            elif "Venue" in text:
                team_data["venue"] = text.split("-")[-1].strip()
            elif "Captain" in text:
                team_data["captain"] = text.split("-")[-1].strip()

    # Extract trophies won
    trophy_div = soup.find("div", class_="vn-trophyBtn")
    if trophy_div:
        trophy_span = trophy_div.find("span")
        if trophy_span:
            team_data["trophies won"] = trophy_span.get_text(strip=True)

    # Extract and categorize players by role
    players = soup.find_all("div", class_="ih-p-img")
    for player in players:
        try:
            # Extract player name
            name = player.find("h2").text.strip()
            # Extract role and normalize text
            role = player.find("span", class_="d-block w-100 text-center").text.strip().lower()
            
            # Add to respective role in dictionary
            if role == "batter":
                roles_dict["Batter"].append(name)
            elif role == "bowler":
                roles_dict["Bowler"].append(name)
            elif role in ["all-rounder", "allrounder"]:  # Handle variations
                roles_dict["All-rounder"].append(name)
        except AttributeError:
            # Skip if any detail is missing
            continue

    # Add roles dictionary to the team data
    team_data["players"] = roles_dict

    # Return the final dictionary
    if not team_data:
        raise HTTPException(status_code=404, detail="No data found for the given team.")
    
    return team_data
