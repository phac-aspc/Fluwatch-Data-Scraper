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
    'PEI': 11,
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
    'NVT.': 61,
    'N.W.T': 61,
    'NU': 62,
    'CANADA': 1
}

def parse_week(text):
    to_parse = text.strip().replace("Januray", "January").replace("Febuary", "February")
    temp_parts = re.split(r"\(|\)| to | – ", to_parse)

    try:
        start = datetime.strptime(temp_parts[1].strip(), "%B %d, %Y").strftime('%B, %d')
    except ValueError:
        try:
            start = datetime.strptime(temp_parts[1].strip(), "%B %d").strftime('%B, %d')
        except:
            start = temp_parts[1].strip()
    try:    
        end = datetime.strptime(temp_parts[2].strip(), "%B %d, %Y").strftime('%B, %d')
    except ValueError:
        try:
            end = datetime.strptime(temp_parts[2].strip(), "%B %d").strftime('%B, %d')
        except:
            end = temp_parts[2].strip()
    try:
        year = datetime.strptime(temp_parts[2].strip(), "%B %d, %Y").strftime('%Y')
    except ValueError:
        try:
            year = datetime.strptime(temp_parts[1].strip(), "%B %d, %Y").strftime('%Y')
        except:
            year = temp_parts[2][-5:]
    return start.replace(',', ''), end.replace(',', ''), year.strip()

class Crawler(object):
    def scrape(self):
        start_url = 'https://www.canada.ca/en/public-health/services/diseases/flu-influenza/influenza-surveillance/weekly-influenza-reports.html'
        f = open('data/figure3.csv', 'a+')
        f.truncate(0)
        headers = [
                    'startDate',
                    'endDate',
                    'year',
                    'province',
                    'pruid',
                    'aTotal',
                    'aH1N1pdm09',
                    'aH3N2',
                    'aUns',
                    'bTotal'
        ]

        header = ','.join(headers)
        f.write(f'{header}\n')

        req = requests.get(start_url)
        soup = BeautifulSoup(req.text, features='html.parser')
        links = soup.find_all(class_='panel-body')[1].find_all('a', href=re.compile("en/public-health/services/diseases/flu-influenza/influenza-surveillance/weekly-reports"))
        for home_url in tqdm(links):
            # getting the first page
            # home_url = 'https://www.canada.ca/en/public-health/services/diseases/flu-influenza/influenza-surveillance/weekly-reports-2017-2018-season.html'
            
            req = requests.get('https://www.canada.ca' + home_url['href'])
            home_html = req.text
            soup = BeautifulSoup(home_html , features='html.parser')

            # getting the urls for each week
            links = soup.find_all('a', href=re.compile(r'/en/public-health/services/publications/diseases-conditions/fluwatch/*'))
            week_urls = ['https://www.canada.ca' + a['href'] for a in links]
                
            for i in tqdm(range(len(week_urls))):
                # make request to weekly url
                try:
                    req = requests.get(week_urls[i])
                except:
                    time.sleep(5)
                    req = req = requests.get(week_urls[i])
                # get the page text
                html = req.text

                soup = BeautifulSoup(html, features='html.parser')
                table = soup.find('figure', id='f3').find('table') 

                try:
                    rows = table.find('tbody').find_all('tr')
                except:
                    try:
                        rows = soup.find('table', id='tf3').find('tbody').find_all('tr')
                    except:
                        rows = soup.find('table', id='t1').find('tbody').find_all('tr')
                try:
                    title = table.find('thead').find_all('tr')[0].find_all('th')[1].text
                except:
                    try:
                        title = soup.find('table', id='tf3').find('thead').find_all('tr')[0].find_all('th')[1].text
                    except:
                        title = soup.find('table', id='t1').find('thead').find_all('tr')[0].find_all('th')[1].text
                # start, end, weeks = parse_week(weeks_info[i])
                start, end, year = parse_week(title)    

                week = ''
                for i in range(len(rows)-1):
                    cells = rows[i].find_all(['th','td'])[0:6]
                    if 'Percentage' not in cells[0].text:
                        values = []
                        for cell in cells:
                            value = cell.text.replace(',', '').replace(' ', '').strip()
                            if 'Footnote' in value:
                                value = 'suppressed'
                            values.append(value)
                            try:
                                values.append(str(SGC[value.upper()]))
                            except KeyError:
                                pass
                            
                        entry = f'"{start}","{end}",{year},{",".join(values)}'
                        week += f'{entry}\n'

                try:
                    f.write(week)
                except Exception as e:
                    print(f'[WEEK WRITE FAILED] {e}')
                    exit()    

if __name__ == '__main__':
    Fire(Crawler)