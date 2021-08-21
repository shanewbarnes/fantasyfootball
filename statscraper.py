# scraping libraries
from bs4 import BeautifulSoup
from urllib.request import urlopen

# data manipulation
import pandas


# header_row handles cases where there are 2 header rows
# schedule flag handles schedule urls, which has and empty list at the beginning of stats list for unknown reason
def get_data(url, header_row=0, schedule_flag=False, flag_2021=False):

    html = urlopen(url)
    page = BeautifulSoup(html, features="html.parser")

    # The [0] at the end of the line makes sure to get only the first row
    # tr = table rows, th = table headers, td = table columns
    headers = page.findAll('tr')[header_row]
    headers = [column.getText() for column in headers.findAll('th')]

    # [1:] gets every thing except for the header
    rows = page.findAll('tr')[header_row + 1:]

    stats = []
    for stat in range(len(rows)):
        stats.append([column.getText() for column in rows[stat].findAll('td')])

    # needs to be stats[1:] and stats[0] for other data
    if schedule_flag:
        if flag_2021:
            stats[0].append('18')
        data = pandas.DataFrame(stats[1:], columns=stats[0])
    else:
        data = pandas.DataFrame(stats, columns=headers[1:])

    return data


def change_team_names(data):

    # makes all team names consistent across all data sources
    team_names_dict = {'Arizona Cardinals': 'ARI', 'Atlanta Falcons': 'ATL', 'Baltimore Ravens': 'BAL',
                       'Buffalo Bills': 'BUF', 'Carolina Panthers': 'CAR', 'Chicago Bears': 'CHI',
                       'Cincinnati Bengals': 'CIN', 'Cleveland Browns': 'CLE', 'Dallas Cowboys': 'DAL',
                       'Denver Broncos': 'DEN', 'Detroit Lions': 'DET', 'Green Bay Packers': 'GB', 'GNB': 'GB',
                       'Houston Texans': 'HOU', 'Indianapolis Colts': 'IND', 'Jacksonville Jaguars': 'JAX',
                       'Kansas City Chiefs': 'KC', 'KAN': 'KC', 'Las Vegas Raiders': 'LV', 'Oakland Raiders': 'LV',
                       'LVR': 'LV', 'OAK': 'LV', 'Los Angeles Rams': 'LAR', 'St. Louis Rams': 'LAR', 'STL': 'LAR',
                       'Los Angeles Chargers': 'LAC', 'San Diego Chargers': 'LAC', 'SDG': 'LAC',
                       'Miami Dolphins': 'MIA', 'Minnesota Vikings': 'MIN', 'New England Patriots': 'NE', 'NWE': 'NE',
                       'New Orleans Saints': 'NO', 'NOR': 'NO', 'New York Giants': 'NYG', 'New York Jets': 'NYJ',
                       'Philadelphia Eagles': 'PHI', 'Pittsburgh Steelers': 'PIT', 'San Francisco 49ers': 'SF',
                       'SFO': 'SF', 'Seattle Seahawks': 'SEA', 'Tampa Bay Buccaneers': 'TB', 'TAM': 'TB',
                       'Tennessee Titans': 'TEN', 'Washington Football Team': 'WSH', 'Washington Redskins': 'WSH',
                       'WAS': 'WSH'}

    data = data.replace(team_names_dict)

    return data


def clean_defense_data(data):
    # gets only the teams column and the first 32 rows
    data = data['Tm'].iloc[:32]
    return data


def clean_qb_data(data):

    # Avoids data error because there are two columns named Yds
    columns = data.columns.values
    columns[-6] = ''
    data.columns = columns

    data = data[['Player', 'Tm', 'Sk', 'Yds']]

    # removes *, +, and spaces for string comparisons
    data['Player'] = data['Player'].str.replace('[*,+, ]', '', regex=True)

    return data


def clean_rb_data(data):

    data = data[['Player', 'Tm', 'Pos']]

    data['Player'] = data['Player'].str.replace('[*,+, ]', '', regex=True)

    qb_indexes = data[(data['Pos'] == 'QB') | (data['Pos'] == 'qb')].index
    data.drop(qb_indexes, inplace=True)

    return data


def clean_wr_data(data):

    data = data[['Player', 'Tm', 'Pos']]

    # removes players who are not receivers
    rb_te_indexes = data[(data['Pos'] == 'TE') | (data['Pos'] == 'RB') | (data['Pos'] == 'te') | (data['Pos'] == 'rb')].index
    data.drop(rb_te_indexes, inplace=True)

    data['Player'] = data['Player'].str.replace('[*,+, ]', '', regex=True)

    return data


def clean_te_data(data):

    data = data[['Player', 'Tm', 'Pos']]

    rb_wr_indexes = data[(data['Pos'] == 'WR') | (data['Pos'] == 'RB') | (data['Pos'] == 'wr') | (data['Pos'] == 'rb')].index
    data.drop(rb_wr_indexes, inplace=True)

    data['Player'] = data['Player'].str.replace('[*,+, ]', '', regex=True)

    return data


def clean_fantasy_data(data):

    data = data[['Player', 'Tm', 'Age', 'G', 'FantPt']]

    data['Player'] = data['Player'].str.replace('[*,+, ]', '', regex=True)

    return data
