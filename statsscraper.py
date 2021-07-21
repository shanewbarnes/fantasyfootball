# scraping libraries
from bs4 import BeautifulSoup
from urllib.request import urlopen

# data manipulation
import pandas

#url = "https://www.pro-football-reference.com/years/2020/passing.htm"
url = "http://www.espn.com/nfl/schedulegrid/_/year/2010"


def get_data(url):

    html = urlopen(url)
    page = BeautifulSoup(html, features="html.parser")

    # The [0] at the end of the line makes sure to get only the first row
    # tr = table rows, th = table headers, td = table columns
    headers = page.findAll('tr')[0]
    headers = [column.getText() for column in headers.findAll('th')]

    # [1:] gets every thing except for the header
    rows = page.findAll('tr')[1:]

    stats = []
    for stat in range(len(rows)):
        stats.append([column.getText() for column in rows[stat].findAll('td')])

    # needs to be stats and headers[1:] for other data
    data = pandas.DataFrame(stats[1:], columns=stats[0])

    return data

print(get_data(url))