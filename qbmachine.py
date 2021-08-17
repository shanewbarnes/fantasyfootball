import dataoperations
import statscraper
import pandas
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

qb_list = []
start_year = 2003
for year in range(start_year, 2020):

    if year == 2014:
        continue

    player_url = "https://www.pro-football-reference.com/years/" + str(year) + "/rushing.htm"
    fantasy_url = "https://www.pro-football-reference.com/years/" + str(year) + "/fantasy.htm"
    schedule_url = "http://www.espn.com/nfl/schedulegrid/_/year/" + str(year)
    defense_url = "https://www.pro-football-reference.com/years/" + str(year) + "/opp.htm"
    prev_year_fantasy_url = "https://www.pro-football-reference.com/years/" + str(year - 1) + "/fantasy.htm"

    player_data = statscraper.get_data(player_url, 0, False)
    fantasy_data = statscraper.get_data(fantasy_url, 1, False)
    schedule_data = statscraper.get_data(schedule_url, 0, True)
    defense_data = statscraper.get_data(defense_url, 1, False)
    prev_year_fantasy_data = statscraper.get_data(prev_year_fantasy_url, 1, False)

    player_data = statscraper.clean_qb_data(player_data)
    fantasy_data = statscraper.clean_fantasy_data(fantasy_data)
    defense_data = statscraper.clean_defense_data(defense_data)
    prev_year_fantasy_data = statscraper.clean_fantasy_data(prev_year_fantasy_data)

    player_data = statscraper.change_team_names(player_data)
    fantasy_data = statscraper.change_team_names(fantasy_data)
    defense_data = statscraper.change_team_names(defense_data)
    prev_year_fantasy_data = statscraper.change_team_names(prev_year_fantasy_data)

    o_line_ranking = dataoperations.get_o_line_ranking(player_data)

    for qb_num in range(40):

        if player_data['Player'][qb_num] is None:
            continue

        qb_fantasy_data = fantasy_data.loc[fantasy_data['Player'] == player_data['Player'][qb_num]]
        qb_schedule = schedule_data.loc[(schedule_data['TEAM'] == player_data['Tm'][qb_num])]
        qb_prev_fantasy = prev_year_fantasy_data.loc[prev_year_fantasy_data['Player'] == player_data['Player'][qb_num]]

        qb_o_line_strength = o_line_ranking[player_data['Tm'][qb_num]]

        # handles cases where there are two players of the same name, in which case it is skipped
        if qb_prev_fantasy.shape[0] > 1 or qb_fantasy_data.shape[0] > 1:
            continue

        # cases where schedule may be empty (2TM)
        if qb_schedule.empty:
            continue

        # tests when player did not play in the next season or did not score points, in which case it is skipped
        if qb_prev_fantasy.empty or qb_prev_fantasy['FantPt'].values == '' or qb_fantasy_data['FantPt'].values == '':
            continue

        qb = dataoperations.QB_RB(qb_fantasy_data, qb_schedule, defense_data, qb_prev_fantasy, qb_o_line_strength)
        qb_list.append(qb.stats)


data = pandas.DataFrame(qb_list, columns=['Name', 'Age', 'PFPPG', 'SOS', 'OLS', 'FPPG'])

y = data['FPPG']
x = data[['Age', 'PFPPG', 'SOS', 'OLS']]

regressor = LinearRegression()

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.08, random_state=0)

regressor.fit(x_train, y_train)

y_pred = regressor.predict(x_test)

new_df = pandas.DataFrame({'Actual': y_test, 'Predicted': y_pred})
print(new_df)