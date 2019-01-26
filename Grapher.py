import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List
from Scraper import Apartment
from Scraper import Building
from ApartmentFilter import Filter
import Historizer
import ApartmentFilter
import Scraper
import os
import math

def graph_all(filter : Filter):
    for i, b in enumerate(Scraper.avalon_buildings):
        plt.figure(i + 1)
        add_to_figure(b, filter)
    plt.show()


def add_to_figure(building : Building, filter : Filter):
    histos = list(Historizer.load_building(building))

    apts_ids = set()
    for da in histos:
        for id in ApartmentFilter.filter_apartments_get_ids(da.apartments, filter):
            apts_ids.add(id)
    x = [h.date for h in histos]
    #x = [d.date.strftime('%m-%d') for d in histos]
    print(x)
    for i, id in enumerate(sorted(apts_ids, key=lambda id:int(id.split('-')[-1][:-1]))):
        print(id)
        plt.subplot(math.ceil(len(apts_ids) / 2), 2,i+1)
        y = list()
        apt_info = ''
        for da in histos:
            for a in da.apartments:
                if a.id == id:
                    apt_info = f'{a.number} - {a.bed} beds - {a.sq_footage} sq ft'
                    y.append(a.price)
                    break
            else:
                y.append(None)
        print(y)
        plt.plot(x, y)
        plt.title(apt_info)
        plt.subplots_adjust(hspace=1, wspace=0.5)


if __name__ == '__main__':
    graph_all(Filter(3500, 5000, 750))
    #dobro_file = os.path.dirname(os.path.realpath(__file__)) + "/dobro_apts.txt"
    #willoughby_file = os.path.dirname(os.path.realpath(__file__)) + "/willoughby_apts.txt"
    #graph(dobro_file, Filter(3000, 4800, 750))
    #graph(willoughby_file, Filter(3000, 5500, 750))

