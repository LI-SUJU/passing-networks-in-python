import json
# from plot1club import draw_plot_for_1_club
team_ids = []
with open("data/eventing/matches/9/281.json", 'r') as file:
    match_data = json.load(file)
    for match in match_data:
        home_team_id = match["home_team"]["home_team_id"]
        away_team_id = match["away_team"]["away_team_id"]
        if home_team_id not in team_ids:
            team_ids.append(home_team_id)
        if away_team_id not in team_ids:
            team_ids.append(away_team_id)
print(len(team_ids))