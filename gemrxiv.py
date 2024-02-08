#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# gemRxiv
# Copyright (C) 2024 by Sven Kochmann
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the  Free  Software  Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program  is  distributed in  the hope that  it will  be useful,
# but  WITHOUT  ANY  WARRANTY;  without even  the implied  warranty of
# MERCHANTABILITY  or  FITNESS  FOR  A  PARTICULAR  PURPOSE.   See the
# GNU General Public License for more details.
#
# You should  have received  a copy of the  GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# This program  extracts the  hidden gems from  chemRxiv to brag about
# them on Twitter and the like.
#
# Feb 2024: ChemRxiv has its own API now:
# https://chemrxiv.org/engage/chemrxiv/public-api/documentation

import argparse
import datetime
import json
import tabulate
import urllib.request

# Argument setup and parsing
parser = argparse.ArgumentParser(
			description = 'gemrxiv extracts the  hidden gems from  chemRxiv to brag about them on Twitter and the like.')

parser.add_argument('-v', '--version', help = 'prints version information', action = 'version', version = 'gemRxiv! 1.1 by Sven Kochmann')
parser.add_argument('-e', '--entries', metavar = 'E', help = 'Number of entries to load, maximum is 50 (default: 50)', type = int, default = 50)
parser.add_argument('-f', '--finish', metavar = 'F', help = 'Only considers entries BEFORE this finishing date (default: today). Should be YYYY-MM-DD format', type = str, default=datetime.datetime.today().strftime('%Y-%m-%d'))
parser.add_argument('-d', '--days', metavar = 'D', help = 'Entries in the D days before the finishing date will not be considered (default: 180)', type = int, default = 180)

args = vars(parser.parse_args())

# Calculate the starting and ending dates
date_end = datetime.date.fromisoformat(args['finish'])
date_start = date_end - datetime.timedelta(days=args['days'])

# According to chemRxiv API 50 items are the maximum
if not 0 < args['entries'] < 51:
    args['entries'] = 50

# Setup the url (chemRxiv API allows exclusions!)
url1 = 'https://chemrxiv.org/engage/chemrxiv/public-api/v1/items?limit=' + str(args['entries']) + '&sort=VIEWS_COUNT_ASC&searchDateFrom=' + date_start.strftime('%Y-%m-%d') + '&searchDateTo=' + date_end.strftime('%Y-%m-%d')

# Opens an url an returns its contents as JSON-dictionary
def http_json_as_dict(urltogo):
    req = urllib.request.Request(url=urltogo, headers={'User-Agent': 'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req))

# Get all results
print('Sending request \'' + url1 + '\'...', flush=True)
print('Downloading preprints...', end='', flush=True)
preliminary_results = http_json_as_dict(url1)["itemHits"]
print('%d loaded.' % len(preliminary_results), flush=True)

# Create a list of dictionaries (article_id, title, views, downloads, publishing date, days since publishing,
# downloads/days) with only the papers that are left; ask statistics for views and downloads
results = []
for index, entry in enumerate(preliminary_results):
    print("Downloading data for preprint %d of %d" % (index + 1, len(preliminary_results)), end='\r')

    # Add entry 
    data = {'id': entry['item']['id'],
            'title': entry['item']['title'],
            'views': entry['item']['metrics'][0]['value'],
            'citations': entry['item']['metrics'][1]['value'], 
            'downloads': entry['item']['metrics'][2]['value'], 
            'date': entry['item']['publishedDate'][0:10],
            'days_online': 0,
            'downloads_per_day': 0.0,
            'url': 'https://chemrxiv.org/engage/chemrxiv/article-details/' + entry['item']['id']}
    results.append(data)

    pass

print("")


for index, entry in enumerate(results):
    year, month, day = entry['date'].split('-')
    days_online = (datetime.date.today() - datetime.date(int(year), int(month), int(day))).days
    results[index]['days_online'] = int(days_online)
    if days_online > 0:
        results[index]['downloads_per_day'] = float(float(entry['downloads'])/float(days_online))

# Sort by downloads
results = sorted(results, key=lambda entry: entry['downloads_per_day'])

print("")
print(tabulate.tabulate(results)) #.encode("ascii", "replace"))



