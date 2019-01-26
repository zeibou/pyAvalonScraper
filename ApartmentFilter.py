from dataclasses import dataclass
from typing import List
from Scraper import Apartment

@dataclass
class Filter:
    min_price : int
    max_price : int
    min_surface : int

def apt_wanted(a : Apartment, filter : Filter):
    return  a.price >= filter.min_price and a.price <= filter.max_price and a.sq_footage >= filter.min_surface

def filter_apartments_get_ids(apartments, filter: Filter):
    ids = set()
    for a in apartments:
        if apt_wanted(a, filter):
            ids.add(a.id)
    return ids

def filter_apartments(apartments, filter: Filter):
    subset = list()
    for a in apartments:
        if apt_wanted(a, filter):
            subset.append(a)
    return subset