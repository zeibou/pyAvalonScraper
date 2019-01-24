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



dobro_code = 'NY037'
willoughby_code = 'NY039'
min_price = 3000
max_price = 10000
json_url = 'https://api.avalonbay.com/json/reply/ApartmentSearch?communityCode='
price_filter = f'&min={min_price}&max={max_price}'
json_url_dobro = f'{json_url}{dobro_code}{price_filter}'
json_url_willoughby = f'{json_url}{willoughby_code}{price_filter}'

def get_apartments(json_url):
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

def print_apts(url):
    print(url)
    for apt in get_apartments(url):
        print(apt)



if __name__ == '__main__':
    print_apts(json_url_dobro)
    print_apts(json_url_willoughby)

