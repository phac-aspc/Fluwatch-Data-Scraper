from bs4 import BeautifulSoup
import requests
from pprint import pprint
import re
import time
from datetime import datetime
from fire import Fire
from tqdm import tqdm

SGC = {
    'NL': 10,
    'PE': 11,
    'NS': 12,
    'NB': 13,
    'QC': 24,
    'ON': 35,
    'MB': 46,
    'SK': 47,
    'AB': 48,
    'BC': 59,
    'YT': 60,
    'NT': 61,
    'NU': 62,
    'CANADA': 1
}

def parse_week(text):
    to_parse = text.strip()
    temp_parts = re.split(r"\(|\)| to | – ", to_parse)
    start = temp_parts[0].strip()
    end = temp_parts[1].strip()
    week = temp_parts[2].lower().replace('weeks', '').strip()
    week = week.replace('week', '').strip()

    return start, end, week

class Crawler(object):
    def scrape(self, target):
        # getting the first page
        home_url = 'https://www.canada.ca/en/public-health/services/diseases/flu-influenza/influenza-surveillance/weekly-reports-2017-2018-season.html'
        
        req = requests.get(home_url)
        home_html = req.text
        soup = BeautifulSoup(home_html , features='html.parser')

        # getting the urls for each week
        links = soup.find_all('a', href=re.compile(r'/en/public-health/services/publications/diseases-conditions/fluwatch/*'))
        week_urls = ['https://www.canada.ca' + a['href'] for a in links]
        weeks_info = [a.text for a in links]

        if target is None:
            pass
        if target == 'f3':
            f = open('data/figure3.csv', 'a+')
            f.truncate(0)
            headers = [
                'startDate',
                'endDate',
                'week',
                'province',
                'pruid',
                'aTotal',
                'aH1N1pdm09',
                'aH3N2',
                'aUns',
                'bTotal'
            ]

        elif target == 'f8':
            f = open('data/figure8.csv', 'a+')
            f.truncate(0)
            headers = [
                'startDate',
                'endDate',
                'week',
                'ageGroup',
                'totalHospitalizations'
            ]
        elif target == 'f9':
            f = open('data/figure9.csv', 'a+')
            f.truncate(0)
            headers = [
                'startDate',
                'endDate',
                'week',
                'ageGroup',
                'totalHospitalizations'
            ]
        
        header = ','.join(headers)
        f.write(f'{header}\n')

        for i in tqdm(range(len(week_urls))):
            # make request to weekly url
            req = requests.get(week_urls[i])
            # get the page text
            html = req.text

            soup = BeautifulSoup(html, features='html.parser')

            if target is None:
                pass
            elif target == 'f3': 
                table = soup.find('figure', id='f3').find('table')
                rows = table.find('tbody').find_all('tr')
                start, end, weeks = parse_week(weeks_info[i])

                week = ''
                for i in range(len(rows)-1):
                    cells = rows[i].find_all(['th','td'])[0:6]
                    values = []
                    for cell in cells:
                        value = cell.text.replace(',', '').strip()
                        values.append(value)
                        try:
                            values.append(str(SGC[value.upper()]))
                        except KeyError:
                            pass
                    # values = [cell.contents[0].strip() if type(cell.contents[0]) == 'str' else cell.text.strip() for cell in cells if cell.contents[0]]
                    
                    entry = f'"{start}","{end}",{weeks},{",".join(values)}'
                    week += f'{entry}\n'
                
                try:
                    f.write(week)
                except Exception as e:
                    print(f'[WEEK {weeks} WRITE FAILED] {e}')
                    exit()

            elif target == 'f8':
                try:
                    table = soup.find('figure', id='f8').find('table')
                    rows = table.find('tbody').find_all('tr')
                    start, end, weeks = parse_week(weeks_info[i])

                    week = ''
                    for i in range(len(rows)-1):
                        cells = rows[i].find_all('td')
                        values = [cell.text for cell in cells]
                        entry = f'"{start}","{end}",{weeks},{",".join(values)}'
                        week += f'{entry}\n'
                    
                    try:
                        f.write(week)
                    except Exception as e:
                        print(f'[WEEK {weeks} WRITE FAILED] {e}')
                        exit()
                except AttributeError:
                    pass
            elif target == 'f9':
                try:
                    table = soup.find('figure', id='f9').find('table')
                    rows = table.find('tbody').find_all('tr')
                    start, end, weeks = parse_week(weeks_info[i])

                    week = ''
                    for i in range(len(rows)-1):
                        cells = rows[i].find_all('td')
                        values = [cell.text for cell in cells]
                        entry = f'"{start}","{end}",{weeks},{",".join(values)}'
                        week += f'{entry}\n'
                    
                    try:
                        f.write(week)
                    except Exception as e:
                        print(f'[WEEK {weeks} WRITE FAILED] {e}')
                        exit()
                except AttributeError:
                    pass

if __name__ == '__main__':
    Fire(Crawler)
