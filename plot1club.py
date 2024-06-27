
import json

from visualization.passing_network import draw_pitch, draw_pass_map
import os
import matplotlib.pyplot as plt

# matches_path = "data/eventing/matches/9/281.json"
# team_id = 904
# team_name = "Bayer Leverkusen"
# match_ids = []

# with open(matches_path, 'r') as file:
#     match_data = json.load(file)
#     for match in match_data:
#         home_team_id = match["home_team"]["home_team_id"]
#         away_team_id = match["away_team"]["away_team_id"]
#         if home_team_id == team_id or away_team_id == team_id:
#             match_ids.append(match["match_id"])
# print the length of the match_ids
# print(len(match_ids))
def draw_plot_for_1_match(match_id, team_name, ax):
    from pandas import json_normalize
    from utils import read_json

    lineups_path = "data/eventing/lineups/{0}.json"
    events_path = "data/eventing/events/{0}.json"

    lineups = read_json(lineups_path.format(match_id))
    names_dict = {player["player_name"]: player["player_nickname"]
                  for team in lineups for player in team["lineup"]}

    events = read_json(events_path.format(match_id))
    df_events = json_normalize(events, sep="_").assign(match_id=match_id)

    if "foul_committed_card_name" in df_events.columns:
        first_red_card_minute = df_events[df_events.foul_committed_card_name.isin(["Second Yellow", "Red Card"])].minute.min()
    else:
        first_red_card_minute = df_events.minute.max()
    first_substitution_minute = df_events[df_events.type_name == "Substitution"].minute.min()
    max_minute = df_events.minute.max()

    num_minutes = min(first_substitution_minute, first_red_card_minute, max_minute)
    # num_minutes

    plot_name = "statsbomb_match{0}_{1}".format(match_id, team_name)

    opponent_team = [x for x in df_events.team_name.unique() if x != team_name][0]
    plot_title ="{0}'s passing network against {1} (StatsBomb eventing data)".format(team_name, opponent_team)

    plot_legend = "Location: pass origin\nSize: number of passes\nColor: number of passes"

    def _statsbomb_to_point(location, max_width=120, max_height=80):
        '''
        Convert a point's coordinates from a StatsBomb's range to 0-1 range.
        '''
        return location[0] / max_width, 1-(location[1] / max_height)

    df_passes = df_events[(df_events.type_name == "Pass") &
                          (df_events.pass_outcome_name.isna()) &
                          (df_events.team_name == team_name) &
                          (df_events.minute < num_minutes)].copy()

    # If available, use player's nickname instead of full name to optimize space in plot
    df_passes["pass_recipient_name"] = df_passes.pass_recipient_name.apply(lambda x: names_dict[x] if names_dict[x] else x)
    df_passes["player_name"] = df_passes.player_name.apply(lambda x: names_dict[x] if names_dict[x] else x)


    df_passes["origin_pos_x"] = df_passes.location.apply(lambda x: _statsbomb_to_point(x)[0])
    df_passes["origin_pos_y"] = df_passes.location.apply(lambda x: _statsbomb_to_point(x)[1])
    player_position = df_passes.groupby("player_name").agg({"origin_pos_x": "median", "origin_pos_y": "median"})

    player_pass_count = df_passes.groupby("player_name").size().to_frame("num_passes")
    player_pass_value = df_passes.groupby("player_name").size().to_frame("pass_value")

    print(player_pass_count.head(10))

    df_passes["pair_key"] = df_passes.apply(lambda x: "_".join(sorted([str(x["player_name"]), str(x["pass_recipient_name"])])), axis=1)
    # df_passes["pair_key"] = df_passes.apply(lambda x: "_".join(sorted([x["player_name"], x["pass_recipient_name"]])), axis=1)
    pair_pass_count = df_passes.groupby("pair_key").size().to_frame("num_passes")
    pair_pass_value = df_passes.groupby("pair_key").size().to_frame("pass_value")

    # print(pair_pass_count.head(10))



    # ax.patch.set_alpha(0.2)
    # ax = draw_pitch()
    ax = draw_pass_map(ax, player_position, player_pass_count, player_pass_value,
                  pair_pass_count, pair_pass_value, plot_title, plot_legend)
    # set transparency of the whole plot
    # ax.patch.set_alpha(0.2)
    # plt.savefig("demo/{0}.png".format(plot_name))
    # plt.savefig("demo/1.png")
    return ax

# ax = draw_pitch()
# for match_id in match_ids:
#     ax = draw_plot_for_1_match(match_id, team_name, ax)
# plt.show()

def draw_plot_for_1_club(team_id, team_name, matches_path):
    match_ids = []

    with open(matches_path, 'r') as file:
        match_data = json.load(file)
        for match in match_data:
            home_team_id = match["home_team"]["home_team_id"]
            away_team_id = match["away_team"]["away_team_id"]
            if home_team_id == team_id or away_team_id == team_id:
                match_ids.append(match["match_id"])
    ax = draw_pitch()
    for match_id in match_ids:
        ax = draw_plot_for_1_match(match_id, team_name, ax)
    print("length of match_ids", len(match_ids))
    plt.show()

