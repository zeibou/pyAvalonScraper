from dataclasses import dataclass
from typing import List
from Scraper import Apartment
import Historizer
import Scraper
import os


@dataclass
class ApartmentChanged:
    apt_before : Apartment
    apt_now : Apartment

def compare(last_apts, new_apts):
    if not last_apts:
        return True
    last_apts_dico = apts_to_dict(last_apts)
    new_apts_dico = apts_to_dict(new_apts)

    removed = list()
    added = list()
    changed = list()
    for id in last_apts_dico:
        if not id in new_apts_dico:
            removed.append(last_apts_dico[id])
        else:
            apt_before = last_apts_dico[id]
            apt_now = new_apts_dico[id]
            if apt_before.price != apt_now.price:
                changed.append(ApartmentChanged(apt_before, apt_now))


    for id in new_apts_dico:
        if not id in last_apts_dico:
            added.append(new_apts_dico[id])


def apts_to_dict(apts : List[Apartment]):
    apts_dico = dict()
    for apt in apts:
        apts_dico[apt.id] = apt
    return apts_dico


if __name__ == '__main__':
    histo_file = os.path.dirname(os.path.realpath(__file__)) + "/histo_apts.txt"
    apts = Scraper.get_apartments(Scraper.json_url_dobro)

    apts_before = Historizer.load(histo_file)