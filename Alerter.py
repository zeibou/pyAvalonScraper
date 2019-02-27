from dataclasses import dataclass
from typing import List
from Scraper import Apartment
from Scraper import Building
from ApartmentFilter import Filter
from Historizer import HistoEntry
import Historizer
import Scraper
import ApartmentFilter
import datetime
import time
import smtplib
import json
import os
from email.mime.text import MIMEText


@dataclass
class ApartmentChanged:
    apt_before : Apartment
    apt_now : Apartment

    def __str__(self):
        price_diff = int(self.apt_now.price - self.apt_before.price)
        sign = '+' if price_diff > 0 else ''
        bath = int(self.apt_now.bath) if self.apt_now.bath == int(self.apt_now.bath) else self.apt_now.bath
        return f'{self.apt_now.number} @ ${int(self.apt_now.price)} ({sign}{price_diff}$) - {self.apt_now.bed} bed {bath} bath - {self.apt_now.sq_footage} sqft - {self.apt_now.avail_date:%B %d}'

@dataclass
class ApartmentUpdates:
    added : List[Apartment]
    removed : List[Apartment]
    changed : List[ApartmentChanged]

@dataclass
class UpdateLog:
    date_before : datetime
    date_after : datetime
    updates : ApartmentUpdates


filters_by_building = {
    Scraper.avalon_buildings[0].id : Filter(3500, 6000, 750),
    Scraper.avalon_buildings[1].id : Filter(3500, 5500, 750)
}

def compare(last_apts, new_apts):
    if last_apts is None:
        return None
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

    return ApartmentUpdates(added, removed, changed)


def apts_to_dict(apts : List[Apartment]):
    apts_dico = dict()
    for apt in apts:
        apts_dico[apt.id] = apt
    return apts_dico

def get_last_snapshot(building : Building):
    histos = list(Historizer.load_building(building))
    if histos:
        return histos[-1]

def print_changes(last_apts, new_apts, filter):
    updates = compare(last_apts, new_apts)
    if updates:
        if updates.added:
            print("New Apartment(s) :")
            for a in ApartmentFilter.filter_apartments(updates.added, filter):
                print(f"   {a}")
        if updates.removed:
            print("Removed Apartment(s) :")
            for a in ApartmentFilter.filter_apartments(updates.removed, filter):
                print(f"   {a}")
        if updates.changed:
            print("Updated Apartment(s) :")
            for aa in updates.changed:
                if ApartmentFilter.apt_wanted(aa.apt_before, filter) or ApartmentFilter.apt_wanted(aa.apt_now, filter) :
                    print(f"   {aa}")


def yield_changes(last_apts, new_apts, filter):
    updates = compare(last_apts, new_apts)
    if updates:
        if updates.added:
            yield "New Apartment(s) :"
            for a in ApartmentFilter.filter_apartments(updates.added, filter):
                yield f"   {a}"
        if updates.removed:
            yield "Removed Apartment(s) :"
            for a in ApartmentFilter.filter_apartments(updates.removed, filter):
                yield f"   {a}"
        if updates.changed:
            yield "Updated Apartment(s) :"
            for aa in updates.changed:
                if ApartmentFilter.apt_wanted(aa.apt_before, filter) or ApartmentFilter.apt_wanted(aa.apt_now, filter) :
                    yield f"   {aa}"


def get_update_logs(building : Building, filter : Filter):
    apts_now = Scraper.get_apartments(building)
    histos = list(Historizer.load_building(building))
    histos.append(HistoEntry(datetime.datetime.utcnow(), apts_now))
    for i in range(1, len(histos)):
        yield UpdateLog(histos[i-1].date, histos[i].date, compare(histos[i-1].apartments, histos[i].apartments))


def check_for_changes(historize = False, sendAlerts = False):
    updates_list = []
    now = datetime.datetime.utcnow()
    for b in Scraper.avalon_buildings:
        new_snap = list(Scraper.get_apartments(b))
        last_snap = get_last_snapshot(b)
        if last_snap:
            apts_before = last_snap.apartments
            #print(f"  comparing apts for building {b},  before: {len(apts_before)} apartments - now: {len(new_snap)} apartments", flush=True)
            updates = compare(apts_before, new_snap)
            if updates and (updates.removed or updates.added or updates.changed):
                print("updates detected", flush=True)
                updates_list.append((b, updates))
                if historize:
                    Historizer.save_building(b, new_snap, now)
    if sendAlerts and updates_list:
        send_alerts(updates_list)


def send_alerts(updates):
    send_email(updates)

def send_email(updates):
    config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "email_config.json")
    with open(config_file, 'r') as file:
        conf = json.load(file)


    sender = conf["sender"]
    password = conf["password"]
    receivers = conf["receivers"]
    subject = "Avalon Apartments Updates"
    body = updates_to_body(updates)

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['To'] = ', '.join(receivers)
    msg['From'] = sender

    # Send the message via our own SMTP server.
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(sender, password)

    s.sendmail(sender, receivers, msg.as_string())
    s.close()


def updates_to_body(updates):
    body = ''
    for building, update in updates:
        body += f'{building.name} :\r\n'
        if update.added:
            body += '   Added :\r\n'
            for u in update.added:
                body += f'    {u}\r\n'
        if update.removed:
            body += '   Removed :\r\n'
            for u in update.removed:
                body += f'    {u}\r\n'
        if update.changed:
            body += '   Changed :\r\n'
            for u in update.changed:
                body += f'    {u}\r\n'
    return body

def continuous_task(sleep_time = 60):
    while True:
        now = datetime.datetime.utcnow()
        print(f"checking at {now}", flush=True)
        check_for_changes(True, True)
        time.sleep(sleep_time)


def print_building_changes(building : Building, filter : Filter):
    apts_now = Scraper.get_apartments(building)  # no filter on api because we prefer filtering later (to compare with before)
    last_histo = get_last_snapshot(building)
    if last_histo:
        apts_before = last_histo.apartments
        print_changes(apts_before, apts_now, filter)


def yield_building_changes(building : Building, filter : Filter):
    apts_now = Scraper.get_apartments(building)  # no filter on api because we prefer filtering later (to compare with before)
    last_histo = get_last_snapshot(building)
    if last_histo:
        apts_before = last_histo.apartments
        return yield_changes(apts_before, apts_now, filter)


if __name__ == '__main__':
    #send_email(None)
    continuous_task(90)
    #for b in Scraper.avalon_buildings:
     #   #print_update_logs(b)
     #   filter = filters_by_building[b.id]
     #   print_building_changes(b, filter)