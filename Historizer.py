from dataclasses_json import dataclass_json
from dataclasses import dataclass
from typing import List
from datetime import datetime
import pprint
import os
import Scraper
from Scraper import Apartment

@dataclass_json
@dataclass
class HistoEntry:
    date : datetime
    apartments : List[Apartment]


def save(histo_file, apartments, date):
    histo = HistoEntry(date, list(apartments))
    with open(histo_file, 'a') as file:
        file.write(histo.to_json() + "\n")


def load(histo_file):
    with open(histo_file, 'r') as file:
        for line in file.readlines():
            histo = HistoEntry.from_json(line)
            pprint.pprint(histo)


if __name__ == '__main__':
    dobro_file = os.path.dirname(os.path.realpath(__file__)) + "/dobro_apts.txt"
    willoughby_file = os.path.dirname(os.path.realpath(__file__)) + "/willoughby_apts.txt"
    print(dobro_file)
    #os.remove(histo_file)
    save(dobro_file, Scraper.get_apartments(Scraper.json_url_dobro), datetime.now())
    save(willoughby_file, Scraper.get_apartments(Scraper.json_url_willoughby), datetime.now())
    load(dobro_file)