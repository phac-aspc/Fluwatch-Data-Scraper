from bs4 import BeautifulSoup
import requests
from pprint import pprint
import re
import time


home_url = 'https://www.canada.ca/en/public-health/services/diseases/flu-influenza/influenza-surveillance/weekly-reports-2018-2019-season.html'
req = requests.get(home_url)
home_html = req.text
soup = BeautifulSoup(home_html , features='html.parser')

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
print(header)
for url in week_urls:
    req = requests.get(url)

    html = req.text

    soup = BeautifulSoup(html, features='html.parser')

    tables = soup.find_all('table')

    # headers = table.find_all('tr')[2].find_all('th')
    # headers = [re.sub(r'[ ]+', ' ', th.text) for th in headers]


    title = soup.find('h1', id='wb-cont').text.replace('FluWatch report:', '').strip()

    temp_parts = re.split(r"\(|\)| to ", title)

    start = temp_parts[0]
    end = temp_parts[1]
    end = end.strip()
    week = temp_parts[2]

    for table in tables:
        caption = table.find('caption')
        if caption != None:
            if 'Cumulative numbers of positive influenza specimens by type, subtype and age-group reported through case-based laboratory reporting' in caption.text:
                rows = table.find_all('tr')
                for i in range(3,len(rows)-1):
                    cells = rows[i].find_all('td')
                    line = f'"{start}","{end}",{week}'
                    
                    for cell in cells:
                        line += f',{cell.text}'
                    print(line)