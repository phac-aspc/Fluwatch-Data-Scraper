from bs4 import BeautifulSoup
import requests
from pprint import pprint
import re
import time
import crayons

# getting the first page
home_url = 'https://www.canada.ca/en/public-health/services/diseases/flu-influenza/influenza-surveillance/weekly-reports-2018-2019-season.html'
req = requests.get(home_url)
home_html = req.text
soup = BeautifulSoup(home_html , features='html.parser')

# getting the urls for each week
week_urls = ['https://www.canada.ca' + a['href'] for a in soup.find_all('a', href=re.compile(r'/en/public-health/services/publications/diseases-conditions/fluwatch/*'))]

headers = [
    'startDate',
    'endDate',
    'weeks',
    'ageGroup',
    'aTotal',
    'aH1pdm09',
    'aH3',
    'aUnS',
    'bTotal',
    'aAndBNumber',
    'aAndbPercentage'
]

header = ','.join(headers)
f = open('data/cumulativeNumberOfPositiveInfluenza.csv', 'a+')
f.write(header)

for url in week_urls:
    req = requests.get(url)
    html = req.text
    soup = BeautifulSoup(html, features='html.parser')

    tables = soup.find_all('table')

    # splitting the period into start date, end date and week numbers
    title = soup.find('h1', id='wb-cont').text.replace('FluWatch report:', '').strip()
    temp_parts = re.split(r"\(|\)| to ", title)
    start = temp_parts[0]
    end = temp_parts[1]
    end = end.strip()
    week = temp_parts[2]

    # scraping the tables
    for table in tables:
        # getting the table "title"
        caption = table.find('caption')
        if caption != None:
            # checking if the table is the one we need
            if 'Cumulative numbers of positive influenza specimens by type, subtype and age-group reported through case-based laboratory reporting' in caption.text:
                rows = table.find_all('tr')
                # collecting the data from each row of the table
                for i in range(3,len(rows)-1):
                    cells = rows[i].find_all('td')
                    line = f'"{start}","{end}",{week}'
                    for cell in cells:
                        line += f',{cell.text}'

                    # writing to file
                    try:
                        f.write(f'\n{line}')
                        print(f'{crayons.green("[ADDED]")} {line}')
                    except:
                        print(f'{crayons.red("[WRITE FAILED]")} {line}')
                    time.sleep(0.01)
f.close()

                    