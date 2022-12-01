import datetime
import json
import sys
import time
import urllib
import xmltodict

import puz
import requests

from .basedownloader import BaseDownloader
from ..util import XWordDLException

class UclickDownloader(BaseDownloader):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.url_blob = None

    def find_by_date(self, dt):
        self.date = dt

        # https://picayune.uclick.com/comics/usaon/data/usaon160105-data.xml
        url_format = dt.strftime('%y%m%d')
        return self.url_blob + url_format + '-data.xml'

    def find_latest(self):
        dt = datetime.datetime.today()
        return self.find_by_date(dt)

    def find_solver(self, url):
        return url

    def fetch_data(self, solver_url):
        res = requests.get(solver_url)
        return res.content

    def process_clues(self, clue_list):
        """Return clue list without any end markers"""

        return clue_list

    def parse_xword(self, xword_data):
        fetched = {}
        j = xmltodict.parse(xword_data)
        j1 = j['crossword']
        for field in ['Title', 'Author', 'Editor', 'Copryight']:
            fetched[field] = j1.get('Author', {}).get('@v', '')
            
        if fetched['Editor']:
            fetched['Author'] = ''.join([fetched.get('Author', ''),
                                 ' / Ed. ',
                                 fetched.get('Editor', '')])

        puzzle = puz.Puzzle()
        puzzle.title = fetched.get('Title', '')
        puzzle.author = fetched['Author']
        puzzle.copyright = fetched.get('Copyright', '')
        puzzle.width = int(j1['Width']['@v'])
        puzzle.height = int(j1['Height']['@v'])

        solution = xword_data.get('AllAnswer', {}).get('@v', '').replace('-', '.')

        puzzle.solution = solution

        fill = ''
        for letter in solution:
            if letter == '.':
                fill += '.'
            else:
                fill += '-'
        puzzle.fill = fill

        across_clues = [(int(v['@cn']), urllib.parse.unquote(v['@c'])) for v in j1['across'].values()]
        down_clues = [(int(v['@cn']), urllib.parse.unquote(v['@c'])) for v in j1['down'].values()]

        clues_list = across_clues + down_clues

        clues_list_stripped = [{'number': clue[0], 'clue':clue[1]} for clue in clues_list]

        clues_sorted = sorted(clues_list_stripped, key=lambda x: x['number'])

        clues = [clue['clue'] for clue in clues_sorted]

        puzzle.clues = clues

        return puzzle

class USAToday2Downloader(UclickDownloader):
    command = 'usa2'
    outlet = 'USA Today'
    outlet_prefix = 'USA Today'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.url_blob = 'https://picayune.uclick.com/comics/usaon/data/usaon'


class Universal2Downloader(UclickDownloader):
    command = 'uni2'
    outlet = 'Universal'
    outlet_prefix = 'Universal'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.url_blob = 'https://picayune.uclick.com/comics/fcx/data/fcx'
        
class LATimes2Downloader(UclickDownloader):
    command = 'lat2'
    outlet = 'Los Angeles Times'
    outlet_prefix = 'LA Times'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.url_blob = 'https://picayune.uclick.com/comics/tmcal/data/tmcal'
        
class Newsday2Downloader(UclickDownloader):
    command = 'nd2'
    outlet = 'Newsday'
    outlet_prefix = 'Newsday'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.url_blob = 'https://picayune.uclick.com/comics/crnet/data/crnet'
        
