"""get the All Time Worldwide Box Office
only top 600, as of Aug 2017."""

from bs4 import BeautifulSoup
import requests
from pathlib import Path
import locale

from help import logging, set_logging, write_json

base_url = 'http://www.the-numbers.com/box-office-records/worldwide/all-movies/cumulative/all-time/{}'
output_p = Path('data/movie_box.json')
num_per_page = 100
# max 19461
total_num = 19461
#selectors:
#page_filling_chart > center > table > tbody > tr:nth-child(1)
# remove center!
main_sele = '#page_filling_chart table tbody tr'
# rank_sele = 'td:nth-of-type(1)'
# year_sele = 'td:nth-of-type(2) > a'
# name_sele = 'td:nth-of-type(3) > b > a'
# world_sele = 'td:nth-of-type(4)'
# dome_sele = 'td:nth-of-type(5)'
# inter_sele = 'td:nth-of-type(6)'
dict_sele = {
    'rank' : 'td:nth-of-type(1)',
    'year' : 'td:nth-of-type(2) > a',
    'name' : 'td:nth-of-type(3) > b > a',
    'world_box' : 'td:nth-of-type(4)',
    'domestic_box' : 'td:nth-of-type(5)',
    'internatonal_box' : 'td:nth-of-type(6)',
}


def get_movie_box(out_p=output_p):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    ret = []
    for idx in range(1, total_num, num_per_page):
        resp = requests.get(base_url.format(idx))
        soup = BeautifulSoup(resp.content, 'html.parser')
        movies = soup.select(main_sele)
        # print(movies)
        logging.info(f'num of movies on page: {len(movies)}')
        for movie in movies:
            m = {} 
            for key in dict_sele:
                value = movie.select(dict_sele[key])[0].get_text()
                if not value:
                    value = None
                elif key == 'rank' or key == 'year':
                    value = locale.atoi(value)
                elif key.endswith('_box'):
                    # print(value)
                    value = int(locale.atof(value[1:]))
                m[key] = value
            ret.append(m)
            logging.info(f'add rank:{m["rank"]}, name:{m["name"]}')
    write_json(out_p, ret)


def main():
    set_logging(stream=True)
    if not output_p.is_file() or True:
        get_movie_box()

#%%
if __name__ == '__main__':
    main()
