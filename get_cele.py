"""get the top 500 'Most Popular Females/Males' from 
IMDb website.
"""
from bs4 import BeautifulSoup
import requests
from pathlib import Path

from help import logging, set_logging, write_json

TOP_CELE_P = Path('data/top_cele.json')

base_url = 'http://www.imdb.com/search/name?gender=male,female&start={}'
num_per_page = 50
selector = '#main > table > tr'
id_sele = 'td.number'
name_sele = 'td.name > a'
desc_sele = 'td.name > span'
bio_sele = 'td.name > span.bio'


def main():
    set_logging(stream=True)
    if not TOP_CELE_P.is_file() or True:
        get_cele()


def get_cele():
    ret = []
    for idx in range(1, 500, num_per_page):
        p_url = base_url.format(idx)
        resp = requests.get(p_url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        persons = soup.select(selector)[1:]
        if len(persons) != num_per_page:
            raise ValueError(f'wrong person length: {len(persons)}')
        for person in persons:
            p = {} 
            p['rank'] = int(person.select(id_sele)[0].get_text()[:-1])
            name = person.select(name_sele)[0]
            p['nconst'] = name.get('href').split('/')[2]
            p['name'] = name.get_text()
            desc = person.select(desc_sele)[0].get_text().split(',', 1)
            p['job'] = desc[0]
            p['knownfor'] = desc[1].strip()
            bio = person.select(bio_sele)
            p['bio'] = bio[0].get_text() if bio else ''
            ret.append(p)
            logging.info(f'add rank:{p["rank"]}, name:{p["name"]}')
    write_json(TOP_CELE_P, ret)

#%%
if __name__ == '__main__':
    main()
