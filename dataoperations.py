# Creates classes for storing player data for processing

class Player:

    def __init__(self, data, schedule, defense_stats, prev_year_fantasy_data, flag_2021):
        self.data = data
        self.prev_year_fantasy_data = prev_year_fantasy_data
        self.schedule = schedule
        self.defense_stats = defense_stats
        self.name = self.get_name()
        self.age = self.get_age()
        self.team = self.get_team()
        self.flag_2021 = flag_2021
        self.fantasy_points = self.get_fantasy_points_per_game(self.data)
        self.prev_year_fantasy_points = self.get_fantasy_points_per_game(self.prev_year_fantasy_data)
        self.strength_of_schedule = self.get_strength_of_schedule()

    def get_name(self):
        return self.data['Player'].values[0]

    def get_age(self):
        # needs to be converted to integer because pandas was returning a dataframe after using loc function
        return int(self.data['Age'])

    def get_team(self):
        return self.data['Tm'].values[0]

    def get_fantasy_points_per_game(self, data):
        return int(data['FantPt'].values) / int(data['G'].values)

    def get_strength_of_schedule(self):

        strength_total = 0
        for team in self.schedule:

            team = self.schedule[team].values[0]

            if team == 'BYE' or team == self.team:
                continue

            # flags strings that have @ at front to signify away games
            at_flag = 0
            if team[0] == '@':
                at_flag = 1

            if self.flag_2021:
                defense_dict = {'PIT': 1, 'LAR': 2, 'WSH': 3, 'TB': 4, 'BAL': 5, 'SF': 6, 'IND': 7, 'BUF': 8, 'NE': 9,
                                'CLE': 10, 'DEN': 11, 'MIA': 12, 'CHI': 13, 'MIN': 14, 'KC': 15, 'LAC': 16, 'CAR': 17,
                                'DAL': 18, 'NO': 19, 'GB': 20, 'DET': 21, 'ARI': 22, 'CIN': 23, 'HOU': 24, 'JAX': 25,
                                'NYG': 26, 'NYJ': 27, 'LV': 28, 'PHI': 29, 'SEA': 30, 'TEN': 31, 'ATL': 32}

                team_strength = defense_dict[team[at_flag:]]
            else:
                team_strength = self.defense_stats.loc[self.defense_stats == team[at_flag:]].index.values

            strength_total += 32 - int(team_strength)

        return strength_total


class QB_RB(Player):

    def __init__(self, data, schedule, defense_stats, prev_year_fantasy_data, o_line_strength, flag_2021):
        Player.__init__(self, data, schedule, defense_stats, prev_year_fantasy_data, flag_2021)
        self.o_line_strength = o_line_strength
        self.stats = [self.name, self.age, self.prev_year_fantasy_points, self.strength_of_schedule,
                      self.o_line_strength,
                      self.fantasy_points]


class WR_TE(Player):

    def __init__(self, data, schedule, defense_stats, prev_year_fantasy_data, qb_strength, flag_2021):
        Player.__init__(self, data, schedule, defense_stats, prev_year_fantasy_data, flag_2021)
        self.qb_strength = qb_strength
        self.stats = [self.name, self.age, self.prev_year_fantasy_points, self.strength_of_schedule, self.qb_strength,
                      self.fantasy_points]


def get_o_line_ranking(sack_data, flag_2021=False):

    if flag_2021:
        o_line_ranking = {'CLE': 1, 'IND': 2, 'NE': 3, 'NO': 4, 'TB': 5, 'DAL': 6, 'KC': 7, 'LAR': 8, 'SF': 9,
                          'DET': 10, 'ARI': 11, 'BAL': 12, 'PHI': 13, 'BUF': 14, 'TEN': 15, 'GB': 16, 'WSH': 17,
                          'LAC': 18, 'SEA': 19, 'HOU': 20, 'DEN': 21, 'NYJ': 22, 'JAX': 23, 'ATL': 24, 'CIN': 25,
                          'LV': 26, 'MIN': 27, 'CHI': 28, 'MIA': 29, 'CAR': 30, 'PIT': 31, 'NYG': 32}

        return o_line_ranking

    team_dict = {}
    for row in sack_data.iterrows():

        if row[1].values[0] is None:
            continue

        team = row[1].values[1]
        sacks = int(row[1].values[2])

        if team in team_dict:
            team_dict[team] += sacks
        else:
            team_dict[team] = sacks

    # sorts the dictionary and returns a list of tuples with (key, value)
    o_line_sorted = sorted(team_dict.items(), key=lambda x: x[1])

    o_line_ranking = {}

    # loop puts teams into rankings from 1 up and accounts for ties
    count = 0
    prev = 0
    for team in o_line_sorted:
        if prev == team[1]:
            o_line_ranking[team[0]] = count
        else:
            count += 1
            o_line_ranking[team[0]] = count

        prev = team[1]

    return o_line_ranking


def get_qb_strength(yds_data, flag_2021=False):

    if flag_2021:
        qb_ranking = {'KC': 1, 'ARI': 2, 'BUF': 3, 'DAL': 4, 'GB': 5, 'SEA': 6, 'BAL': 7, 'TB': 8, 'LAC': 9,
                      'LAR': 10, 'TEN': 11, 'MIN': 12, 'CIN': 13, 'PHI': 14, 'JAX': 15, 'ATL': 16, 'PIT': 17,
                      'WSH': 18, 'SF': 19, 'NYG': 20, 'CLE': 21, 'IND': 22, 'MIA': 23, 'LV': 24, 'CHI': 25,
                      'CAR': 26, 'NO': 27, 'DEN': 28, 'NE': 29, 'DET': 30, 'NYJ': 31, 'HOU': 32}

        return qb_ranking

    team_dict = {}
    for row in yds_data.iterrows():

        if row[1].values[0] is None:
            continue

        team = row[1].values[1]
        yds = int(row[1].values[3])

        if team in team_dict:
            team_dict[team] += yds
        else:
            team_dict[team] = yds

    # sorts the dictionary and returns a list of tuples with (key, value)
    qb_sorted = sorted(team_dict.items(), key=lambda x: x[1], reverse=True)

    qb_ranking = {}

    # loop puts teams into rankings from 1 up and accounts for ties
    count = 0
    prev = 0
    for team in qb_sorted:
        if prev == team[1]:
            qb_ranking[team[0]] = count
        else:
            count += 1
            qb_ranking[team[0]] = count

        prev = team[1]

    return qb_ranking
