# %%
# Make sure that the path is the root of the project (it can be checked with '%pwd')

# %cd ..

# %%
from pandas import json_normalize
from utils import read_json

# %%
lineups_path = "data/eventing/lineups/{0}.json"
events_path = "data/eventing/events/{0}.json"

team_name = "Barcelona"
match_id = 15946

# %% [markdown]
# ### Step 1: Read data

# %%
lineups = read_json(lineups_path.format(match_id))
names_dict = {player["player_name"]: player["player_nickname"]
              for team in lineups for player in team["lineup"]}

names_dict
# print(names_dict)
# %%
events = read_json(events_path.format(match_id))
df_events = json_normalize(events, sep="_").assign(match_id=match_id)

# df_events.head()
# print(df_events.head())
# %% [markdown]
# ### Step 2: Compute max. minutes

# %%
first_red_card_minute = df_events[df_events.foul_committed_card_name.isin(["Second Yellow", "Red Card"])].minute.min()
first_substitution_minute = df_events[df_events.type_name == "Substitution"].minute.min()
max_minute = df_events.minute.max()

num_minutes = min(first_substitution_minute, first_red_card_minute, max_minute)
num_minutes
# print("num_minutes", num_minutes)

# %% [markdown]
# ### Step 3: Set text information

# %%
plot_name = "statsbomb_match{0}_{1}".format(match_id, team_name)

opponent_team = [x for x in df_events.team_name.unique() if x != team_name][0]
plot_title ="{0}'s passing network against {1} (StatsBomb eventing data)".format(team_name, opponent_team)

plot_legend = "Location: pass origin\nSize: number of passes\nColor: number of passes"

# %% [markdown]
# ### Step 4: Prepare data

# %%
def _statsbomb_to_point(location, max_width=120, max_height=80):
    '''
    Convert a point's coordinates from a StatsBomb's range to 0-1 range.
    '''
    return location[0] / max_width, 1-(location[1] / max_height)

# %%
df_passes = df_events[(df_events.type_name == "Pass") &
                      (df_events.pass_outcome_name.isna()) &
                      (df_events.team_name == team_name) &
                      (df_events.minute < num_minutes)].copy()

# If available, use player's nickname instead of full name to optimize space in plot
df_passes["pass_recipient_name"] = df_passes.pass_recipient_name.apply(lambda x: names_dict[x] if names_dict[x] else x)
df_passes["player_name"] = df_passes.player_name.apply(lambda x: names_dict[x] if names_dict[x] else x)

# df_passes.head()
# print(df_passes.head(10))
# %%
df_passes["origin_pos_x"] = df_passes.location.apply(lambda x: _statsbomb_to_point(x)[0])
df_passes["origin_pos_y"] = df_passes.location.apply(lambda x: _statsbomb_to_point(x)[1])
player_position = df_passes.groupby("player_name").agg({"origin_pos_x": "median", "origin_pos_y": "median"})

# print(player_position.head(10))

# %%
player_pass_count = df_passes.groupby("player_name").size().to_frame("num_passes")
player_pass_value = df_passes.groupby("player_name").size().to_frame("pass_value")

print(player_pass_count.head(10))

# %%
df_passes["pair_key"] = df_passes.apply(lambda x: "_".join(sorted([str(x["player_name"]), str(x["pass_recipient_name"])])), axis=1)
# df_passes["pair_key"] = df_passes.apply(lambda x: "_".join(sorted([x["player_name"], x["pass_recipient_name"]])), axis=1)
pair_pass_count = df_passes.groupby("pair_key").size().to_frame("num_passes")
pair_pass_value = df_passes.groupby("pair_key").size().to_frame("pass_value")

# print(pair_pass_count.head(10))

# %% [markdown]
# ### Step 5: Plot passing network

# %%
from visualization.passing_network import draw_pitch, draw_pass_map
import matplotlib.pyplot as plt


ax = draw_pitch()
ax = draw_pass_map(ax, player_position, player_pass_count, player_pass_value,
              pair_pass_count, pair_pass_value, plot_title, plot_legend)
plt.savefig("demo/{0}.png".format(plot_name))
# plt.savefig("demo/1.png")

# %%


# %%



