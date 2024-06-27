import json
from plot1club import draw_plot_for_1_club
# make a dictionary of team names and ids
team_ids = []
team_names = {}
path = "data/eventing/matches/9/27.json"
with open(path, 'r') as file:
    match_data = json.load(file)
    for match in match_data:
        home_team_id = match["home_team"]["home_team_id"]
        away_team_id = match["away_team"]["away_team_id"]
        if home_team_id not in team_ids:
            team_ids.append(home_team_id)
            # change the id into a string
            home_team_id = str(home_team_id)
            team_names[home_team_id] = match["home_team"]["home_team_name"]
        if away_team_id not in team_ids:
            team_ids.append(away_team_id)
            # change the id into a string
            away_team_id = str(away_team_id)
            team_names[away_team_id] = match["away_team"]["away_team_name"]
for team_id in team_ids:
    draw_plot_for_1_club(team_id, team_names[str(team_id)], path)
# draw_plot_for_1_club(904, "Bayer Leverkusen", path)
# draw_plot_for_1_club(169, "Bayern Munich", path)
print(team_names)