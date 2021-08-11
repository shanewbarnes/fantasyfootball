import dataoperations
import statscraper
import pandas
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

qb_list = []
start_year = 2002
for year in range(start_year, 2019):

    passing_url = "https://www.pro-football-reference.com/years/" + str(year) + "/passing.htm"
    fantasy_url = "https://www.pro-football-reference.com/years/" + str(year) + "/fantasy.htm"
    schedule_url = "http://www.espn.com/nfl/schedulegrid/_/year/" + str(year)
    defense_url = "https://www.pro-football-reference.com/years/" + str(year) + "/opp.htm"
    next_year_fantasy_url = "https://www.pro-football-reference.com/years/" + str(year + 1) + "/fantasy.htm"

    passing_data = statscraper.get_data(passing_url, 0, False)
    fantasy_data = statscraper.get_data(fantasy_url, 1, False)
    schedule_data = statscraper.get_data(schedule_url, 0, True)
    defense_data = statscraper.get_data(defense_url, 1, False)
    next_year_fantasy_data = statscraper.get_data(next_year_fantasy_url, 1, False)

    passing_data = statscraper.clean_qb_data(passing_data)
    fantasy_data = statscraper.clean_fantasy_data(fantasy_data)
    defense_data = statscraper.clean_defense_data(defense_data)
    next_year_fantasy_data = statscraper.clean_fantasy_data(next_year_fantasy_data)

    dataoperations.get_o_line_ranking(passing_data)
    for qb_num in range(32):
        qb = dataoperations.QB(fantasy_data.loc[fantasy_data['Player'] == passing_data['Player'][qb_num]], schedule_data.loc[(schedule_data['TEAM'] == passing_data['Tm'][qb_num])], defense_data, passing_data['QBR'][qb_num])
        qb_list.append(qb.stats)


data = pandas.DataFrame(qb_list, columns=['Age', 'Fantasy PPG', 'SOS', 'OLS', 'QBR'])

