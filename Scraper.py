import requests
import json

url = 'https://www.avaloncommunities.com/new-york/brooklyn-apartments/ava-dobro/floor-plans#bedrooms-2'

dobro_code = 'NY037'
willoughby_code = 'NY039'
min_price = 3000
max_price = 10000
json_url = 'https://api.avalonbay.com/json/reply/ApartmentSearch?communityCode='
price_filter = f'&min={min_price}&max={max_price}'
json_url_dobro = f'{json_url}{dobro_code}{price_filter}'
json_url_willoughby = f'{json_url}{willoughby_code}{price_filter}'

def print_json(json_url):
    print(json_url)
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
                    pprint_apt(apt)
    print()


def pprint_apt(apt):
    print(apt['apartmentNumber'], apt['pricing']['effectiveRent'], apt['pricing']['availableDate'], apt['hasPromotion'], apt['apartmentSize'], apt['beds'], apt['baths'], apt['unitKey'])


print_json(json_url_dobro)
print_json(json_url_willoughby)

