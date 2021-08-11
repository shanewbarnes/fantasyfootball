# Creates classes for storing player data for processing

class Player:

    def __init__(self, data, schedule, defense_stats):
        self.data = data
        self.schedule = schedule
        self.defense_stats = defense_stats
        self.age = self.get_age()
        self.fantasy_points = self.get_fantasy_points_per_game()
        self.strength_of_schedule = self.get_strength_of_schedule()

    def get_age(self):
        # needs to be converted to integer because pandas was returning a dataframe after using loc function
        return int(self.data['Age'])

    def get_team(self):
        return self.data['Tm'].values[0]

    def get_fantasy_points_per_game(self):
        return int(self.data['FantPt']) / int(self.data['G'])

    def get_strength_of_schedule(self):

        strength_total = 0
        for team in self.schedule:

            team = self.schedule[team].values[0]

            if team == 'BYE' or team == self.get_team():
                continue

            # flags strings that have @ at front to signify away games
            at_flag = 0
            if team[0] == '@':
                at_flag = 1

            team_strength = self.defense_stats.loc[self.defense_stats == team[at_flag:]].index.values

            strength_total += 32 - team_strength[0]

        return strength_total


class QB(Player):

    def __init__(self, data, schedule, defense_stats, qb_rate):
        Player.__init__(self, data, schedule, defense_stats)
        self.qb_rate = qb_rate
        self.o_line_strength = get_o_line_ranking(data)
        self.stats = [self.age, self.fantasy_points, self.strength_of_schedule, self.o_line_strength, self.qb_rate]


class RB(Player):

    def __init__(self, name, data, year, fantasyPoints, opponentStrength, oLineStrength):
        # Player.__init__(name, data)
        self.oLineStrength = oLineStrength


class WR_TE(Player):

    def __init__(self, name, age, year, fantasyPoints, opponentStrength, qbStrength):
        # Player.__init__(name, age, year, fantasyPoints, opponentStrength)
        self.qbStrength = qbStrength


def get_o_line_ranking(sack_data):

    team_dict = {}

    for row in sack_data.iterrows():

        if row[1].values[0] is None:
            continue

        team = row[1].values[1]
        sacks = int(row[1].values[3])

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
