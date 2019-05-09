# Scraping Figure 3
from bs4 import BeautifulSoup
import requests
from pprint import pprint
import re
import time
import crayons

def scrape_figure3(html):
    soup = BeautifulSoup(html, features='html.parser')
    
    headers = [
        'startDate',
        'endDate',
        'weeks'
        'province',
        'aTotal',
        ''
    ]

    table = soup.find('figure', id='f3').find('table')
    rows = table.find('tbody').find_all('tr')
    for row in rows:
        cells = row.find_all(['th','td'])
        values = [cell.contents[0].strip() if type(cell.contents[0]) == 'str' else cell.text.strip() for cell in cells if cell.contents[0]]
        entry = ','.join(values)
        print(entry, end='\n')

if __name__ == '__main__':
    # getting the first page
    home_url = 'https://www.canada.ca/en/public-health/services/diseases/flu-influenza/influenza-surveillance/weekly-reports-2018-2019-season.html'
    req = requests.get(home_url)
    home_html = req.text
    soup = BeautifulSoup(home_html , features='html.parser')

    # getting the urls for each week
    week_urls = ['https://www.canada.ca' + a['href'] for a in soup.find_all('a', href=re.compile(r'/en/public-health/services/publications/diseases-conditions/fluwatch/*'))]

    for url in week_urls:
        req = requests.get(url)
        html = req.text
        scrape_figure3(html)
