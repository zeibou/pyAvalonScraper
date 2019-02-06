from dataclasses_json import dataclass_json
from dataclasses import dataclass
from typing import List
from datetime import datetime
import pprint
import os
import Scraper
from Scraper import Apartment
from Scraper import Building

@dataclass_json
@dataclass
class HistoEntry:
    date : datetime
    apartments : List[Apartment]


def save_file(histo_file, apartments, date):
    histo = HistoEntry(date, list(apartments))
    with open(histo_file, 'a') as file:
        file.write(histo.to_json() + "\n")


def load_file(histo_file):
    with open(histo_file, 'r') as file:
        for line in file.readlines():
            yield HistoEntry.from_json(line)


def histo_file(building : Building, directory = None):
    histo_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'histos') if not directory else directory
    return os.path.join(histo_directory, f'{building.id}.txt')


def save_all(directory = None):
    now = datetime.now()
    for building in Scraper.avalon_buildings:
        apartments = Scraper.get_apartments(building)
        save_building(building, apartments, now, directory)


def save_building(building: Building, apartments, now, directory = None):
    file = histo_file(building, directory)
    save_file(file, apartments, now)


def load_building(building : Building, directory = None):
    file = histo_file(building, directory)
    return load_file(file)


if __name__ == '__main__':
    test_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'histos_test')
    save_all(test_folder)
    for b in Scraper.avalon_buildings:
        pprint.pprint(list(load_building(b, test_folder)))