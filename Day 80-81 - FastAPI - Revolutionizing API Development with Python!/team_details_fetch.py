import requests 

team = 'CSK'


response = requests.get(f"http://127.0.0.1:8000/team-info?team={team}")
output = response.json()
print(output) 