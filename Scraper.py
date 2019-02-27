import requests
import json
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from datetime import datetime


@dataclass_json
@dataclass
class Apartment:
    id : str
    number : str
    price : float
    avail_date : datetime
    sq_footage : int
    bed : int
    bath : float

    def __str__(self):
        bath = int(self.bath) if self.bath == int(self.bath) else self.bath
        return f'{self.number} @ {int(self.price)} - {self.bed} bed {bath} bath - {self.sq_footage} sqft - {self.avail_date:%B %d}'


@dataclass
class Building:
    id : str
    name : str


avalon_buildings = [
    Building('NY037', 'Brooklyn - Ava Dobro'),
    Building('NY039', 'Brooklyn - Willoughby'),
    Building('NY011', 'Long Island City - Avalon Riverview')
]


def get_api_url(building : Building, min_price = 0, max_price = 0):
    json_base_url = 'https://api.avalonbay.com/json/reply/ApartmentSearch?communityCode='
    price_filter_min = f'&min={min_price}' if min_price else ''
    price_filter_max = f'&max={max_price}' if max_price else ''
    return f'{json_base_url}{building.id}{price_filter_min}{price_filter_max}'


def get_apartments(building : Building, min_price = 0, max_price = 0):
    json_url = get_api_url(building, min_price, max_price)
    r = requests.get(json_url)
    parsed_json = json.loads(r.content.decode('utf-8'))
    results = parsed_json['results']
    availableFloorPlanTypes = results['availableFloorPlanTypes']
    for floorPlanType in availableFloorPlanTypes:
        availableFloorPlans = floorPlanType['availableFloorPlans']
        for plan in availableFloorPlans:
            finishPackages = plan['finishPackages']
            for item in finishPackages:
                apartments = item['apartments']
                for apt in apartments:
                    yield Apartment(apt['unitKey'],
                                      apt['apartmentNumber'],
                                      apt['pricing']['effectiveRent'],
                                      datetime.fromtimestamp(int(apt['pricing']['availableDate'][6:-2]) / 1000),
                                      apt['apartmentSize'],
                                      apt['beds'],
                                      apt['baths'])

def print_apts(building  : Building):
    url = get_api_url(building)
    print(url)
    for apt in sorted(get_apartments(building), key=lambda a:a.price):
        print(apt)
    print()

if __name__ == '__main__':
    for b in avalon_buildings:
        print_apts(b)

