"""
RA scraper
July 2019
"""

from requests import get
from bs4 import BeautifulSoup as Soup
import pandas as pd
import re
import tqdm
from typing import Dict

hdr = {
    'User-Agent': 'Chrome/75.0.3770.100',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Referer': 'https://cssspritegenerator.com',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}

url = 'https://www.residentadvisor.net/clubs.aspx'
d = get(url, headers=hdr)
soup = Soup(d.content, 'html.parser')


def get_info(url: str) -> Dict:
    """get club info from url and return as dict"""

    res = dict()
    d = get(url, headers=hdr)
    soup = Soup(d.content, 'html.parser')
    res['title'] = soup.find('span', attrs={"itemprop": "name"})
    res['address'] = soup.find('span', attrs={"itemprop": "street-address"})
    pattern = '(GIR ?0AA|[A-PR-UWYZ]([0-9]{1,2}|([A-HK-Y][0-9]([0-9ABEHMNPRV-Y])?)' \
              '|[0-9][A-HJKPS-UW]) ?[0-9][ABD-HJLNP-UW-Z]{2})'

    for i in soup.find_all('li'):
        if 'Capacity' in i.text:
            res['capacity'] = int(re.sub("\D", "", i.text))
    # res['about'] = soup.find('div', attrs={'class': 'pr24 pt8'})

    if res['title']:
        res['title'] = res['title'].text
    # if res['about']:
    #     res['about'] = res['about'].text.replace('\n', '')
    if res['address']:
        res['address'] = res['address'].text.replace('\xa0', '')
        res['postcode'] = re.search(pattern, res['address'])
        if res['postcode']:
            res['postcode'] = res['postcode'].group(0)
    return res


df_list = []
for i in tqdm.tqdm(soup.find_all("div", {"class": "fl"})[1:]):
    try:
        page = i.find('a', href=True)['href']
    except TypeError: continue
    if 'club' in page:
        info_dict = get_info('https://www.residentadvisor.net'+page)
        df_list.append(info_dict)

df = pd.DataFrame(df_list)
print(df.head())
df.to_csv('results.csv', index=False)

df.dropna(how='any', inplace=True)
df = df[(df['postcode'].str[0]=='N')|(df['postcode'].str[0]=='E')]
df = df[df['capacity'] <= 150]
df.reset_index(drop=True, inplace=True)
df.to_csv('shortlist.csv', index=False)