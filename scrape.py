#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import urllib
from datetime import datetime
from bs4 import BeautifulSoup
from json import dumps
import re

base_url = 'http://o2.mobile.idos.cz'
headers = { 'User-Agent' : 'Mozilla/5.0' }


def get_path(start='', end='', date=None, time=None, resource=None, default_resource='/pid/spojeni/'):
    """
    start: Starting station
    end: Finish
    date: dd.mm.yyyy
    time: HH:MM
    """
    date_format = '%d.%m.%Y'
    if date is None:
        date = datetime.now().strftime(date_format)
    else:
        date = datetime.strptime(date, date_format).strftime(date_format)

    time_format = '%H:%M'
    if time is None:
        time = datetime.now().strftime(time_format)
    else:
        time = datetime.strptime(time, time_format).strftime(time_format)

    data = {
        'FROM_0t': start,
        'TO_0t': end,
        'form-datum': date,
        'form-cas': time,
        'cmdSearch': u'Hledat'
    }

    if resource is None:
        request = urllib2.Request(base_url+default_resource, urllib.urlencode(data), headers)
    else:
        request = urllib2.Request(base_url+resource, None, headers)

    response = urllib2.urlopen(request)
    doc = BeautifulSoup(response)

    response = {}

    resource_footer = doc.find('div', {'class': 'botanch'})
    if resource_footer:
        previous_resource = resource_footer.find('a')
        next_resource = previous_resource.findNext('a')
        response['next'] = '/path?resource='+urllib.quote_plus(next_resource['href']),
        response['previous'] = '/path?resource='+urllib.quote_plus(previous_resource['href'])
    response['path'] = parse_path(doc)

    return response


def parse_path(doc, expand_details=False):
    routes = []
    for path in doc.findAll('table', attrs={'class': 'conntbl'}):
        subroute = []
        stations = []
        summary = path.findAll('tr')[-1].text
        duration = re.search(ur'·(.*?)\,', summary).group(1).strip()
        distance = re.search(ur'\,(.*?)\,', summary).group(1).strip()
        price = re.search(ur'\km,(.*?)·', summary).group(1).strip()
        summary = {'distance': distance, 'duration': duration, 'price': price}

        for step in path.findAll('tr'):
            transport = step.findAll('span', {'class': 'train'})
            for s in transport:
                detail = s.findNext('a')['href']
                if expand_details:
                    detail = get_detail(detail)
                else:
                    detail = '/detail?resource='+urllib.quote_plus(detail)
            transport = [o.text for o in transport]
            for station in step.findAll('td', {'class': 'ar'}):
                name = station.previous_sibling.text.strip()
                arrival = station.text.strip()
                stations.append({'name': name, 'arrival': arrival})
            if transport:
                subroute.append({'type': transport.pop().strip(), 'stations': stations, 'detail': detail})
                stations = []
        routes.append({'route':subroute, 'summary': summary})
    return routes

def get_detail(resource):
    detail = []
    request = urllib2.Request(base_url+resource, None, headers)
    response = urllib2.urlopen(request)
    doc = BeautifulSoup(response)
    for station in doc.findAll('tr', {'class': 'bbot'}):
        name = station.findNext('td')
        arrival = name.findNext('td')
        if 'bold' in station['class']:
            marked = True
        else:
            marked = False
        detail.append({'name': name.text, 'arrival': arrival.text, 'marked': marked})
    return detail
