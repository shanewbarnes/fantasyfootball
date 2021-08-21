import dataoperations
import statscraper
import pandas
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

QB = False
RB = True
WR = False
TE = False

player_list = []
for year in range(2002, 2022):

    print(year)
    # 2014 is skipped due to inconvenient layout on schedule website
    if year == 2014:
        continue

    flag_2021 = False
    if year == 2021:
        flag_2021 = True
        year -= 1

    passing_url = "https://www.pro-football-reference.com/years/" + str(year) + "/passing.htm"
    if QB:
        player_url = "https://www.pro-football-reference.com/years/" + str(year) + "/passing.htm"
        player_data = statscraper.get_data(player_url)
        player_data = statscraper.clean_qb_data(player_data)
    elif RB:
        player_url = "https://www.pro-football-reference.com/years/" + str(year) + "/rushing.htm"
        player_data = statscraper.get_data(player_url, 1)
        player_data = statscraper.clean_rb_data(player_data)
    elif WR or TE:
        player_url = "https://www.pro-football-reference.com/years/" + str(year) + "/receiving.htm"
        player_data = statscraper.get_data(player_url)
        if WR:
            player_data = statscraper.clean_wr_data(player_data)
        elif TE:
            player_data = statscraper.clean_te_data(player_data)

    fantasy_url = "https://www.pro-football-reference.com/years/" + str(year) + "/fantasy.htm"
    defense_url = "https://www.pro-football-reference.com/years/" + str(year) + "/opp.htm"

    if flag_2021:
        year += 1

    prev_year_fantasy_url = "https://www.pro-football-reference.com/years/" + str(year - 1) + "/fantasy.htm"
    schedule_url = "http://www.espn.com/nfl/schedulegrid/_/year/" + str(year)

    passing_data = statscraper.get_data(passing_url)
    fantasy_data = statscraper.get_data(fantasy_url, 1)
    defense_data = statscraper.get_data(defense_url, 1)
    prev_year_fantasy_data = statscraper.get_data(prev_year_fantasy_url, 1)

    # extra games in 2021 season requires the data to be scraped differently
    if flag_2021:
        schedule_data = statscraper.get_data(schedule_url, 0, True, True)
    else:
        schedule_data = statscraper.get_data(schedule_url, 0, True)

    passing_data = statscraper.clean_qb_data(passing_data)
    fantasy_data = statscraper.clean_fantasy_data(fantasy_data)
    defense_data = statscraper.clean_defense_data(defense_data)
    prev_year_fantasy_data = statscraper.clean_fantasy_data(prev_year_fantasy_data)

    player_data = statscraper.change_team_names(player_data)
    passing_data = statscraper.change_team_names(passing_data)
    fantasy_data = statscraper.change_team_names(fantasy_data)
    defense_data = statscraper.change_team_names(defense_data)
    prev_year_fantasy_data = statscraper.change_team_names(prev_year_fantasy_data)

    if QB or RB:
        o_line_ranking = dataoperations.get_o_line_ranking(passing_data)
        if year == 2021:
            o_line_ranking = dataoperations.get_o_line_ranking(passing_data, True)

    elif WR or TE:
        qb_ranking = dataoperations.get_qb_strength(passing_data)
        if year == 2021:
            qb_ranking = dataoperations.get_qb_strength(passing_data, True)

    for player_num in range(40):

        if player_num not in player_data.index:
            continue

        if player_data['Player'][player_num] is None:
            continue

        player_fantasy_data = fantasy_data.loc[fantasy_data['Player'] == player_data['Player'][player_num]]
        player_schedule = schedule_data.loc[(schedule_data['TEAM'] == player_data['Tm'][player_num])]
        player_prev_fantasy = prev_year_fantasy_data.loc[
            prev_year_fantasy_data['Player'] == player_data['Player'][player_num]]

        # handles cases where there are two players of the same name, in which case it is skipped
        if player_prev_fantasy.shape[0] > 1 or player_fantasy_data.shape[0] > 1:
            continue

        # cases where schedule may be empty (2TM)
        if player_schedule.empty:
            continue

        # tests when player did not play in the next season or did not score points, in which case it is skipped
        if player_prev_fantasy.empty or player_fantasy_data.empty or player_prev_fantasy['FantPt'].values == '' or player_fantasy_data['FantPt'].values == '':
            continue

        if QB or RB:
            player_o_line_strength = o_line_ranking[player_data['Tm'][player_num]]

            player = dataoperations.QB_RB(player_fantasy_data, player_schedule, defense_data, player_prev_fantasy,
                                              player_o_line_strength, flag_2021)
        else:
            player_qb_strength = qb_ranking[player_data['Tm'][player_num]]

            player = dataoperations.WR_TE(player_fantasy_data, player_schedule, defense_data, player_prev_fantasy,
                                              player_qb_strength, flag_2021)

        player_list.append(player.stats)

if QB or RB:
    data = pandas.DataFrame(player_list, columns=['Name', 'Age', 'PFPPG', 'SOS', 'OLS', 'FPPG'])
    y = data['FPPG']
    x = data[['Age', 'PFPPG', 'SOS', 'OLS']]
elif WR or TE:
    data = pandas.DataFrame(player_list, columns=['Name', 'Age', 'PFPPG', 'SOS', 'QBS', 'FPPG'])
    y = data['FPPG']
    x = data[['Age', 'PFPPG', 'SOS', 'QBS']]

regressor = RandomForestRegressor(n_estimators=1000, max_depth=80)

# QB parse: 579
# RB parse: 576
# WR parse: 977
# TE parse:

data = data[576:]
x_train = x[:576]
x_test = x[576:]
y_train = y[:576]
y_test = y[576:]

regressor.fit(x_train, y_train)

y_pred = regressor.predict(x_test)

data['Predicted'] = y_pred

data.to_csv(r'C:\Projects\fantasyfootball\rbdata.csv')

data = data.sort_values(by=['Predicted'], ascending=False)
data.to_csv(r'C:\Projects\fantasyfootball\rbdata.csv', mode='a')
data = data.sort_values(by=['FPPG'], ascending=False)
data.to_csv(r'C:\Projects\fantasyfootball\rbdata.csv', mode='a')
