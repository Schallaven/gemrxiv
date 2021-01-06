#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# gemRxiv
# Copyright (C) 2020 by Sven Kochmann
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

import argparse
import datetime
import json
import tabulate
import urllib.request

# Argument setup and parsing
parser = argparse.ArgumentParser(
			description = 'gemrxiv extracts the  hidden gems from  chemRxiv to brag about them on Twitter and the like.')

parser.add_argument('-v', '--version', help = 'prints version information', action = 'version', version = 'gemRxiv! 1.1 by Sven Kochmann')
parser.add_argument('-e', '--entries', metavar = 'E', help = 'Number of entries to load, maximum is 1000 (default: 1000)', type = int, default = 1000)
parser.add_argument('-d', '--days', metavar = 'D', help = 'Entries in the last D days will not be considered (default: 180)', type = int, default = 180)
parser.add_argument('-n', '--nocut', help = 'Do not cut entries, i.e. consider all entries.', action = 'store_true', default = False)

args = vars(parser.parse_args())

# Calculate the date 
date_cutoff = datetime.datetime.today() - datetime.timedelta(days=args['days'])

# According to Figshare API page_size=1000 is the maximum
if not 0 < args['entries'] < 1001:
    args['entries'] = 100

# Setup the two url, one for all entries and one for the entries to exclude (Figshare
# does not have a direct function to exclude entries; or at least I did not find one)
# According to Figshare API item_type = 12 are pre-prints and all chemRxiv pre-prints 
# have group = 13668
url1 = 'https://api.figshare.com/v2/articles?group=13668&page_size=' + str(args['entries']) + '&order=published_date&order_direction=desc'
url2 = url1 + '&published_since=' + date_cutoff.strftime('%Y-%m-%d')

# Opens an url an returns its contents as JSON-dictionary
def http_json_as_dict(url):
    return json.load(urllib.request.urlopen(url))

# Get all results
print('Downloading preprints...', end='', flush=True)
preliminary_results = http_json_as_dict(url1)
print('%d loaded.' % len(preliminary_results), flush=True)

# These results will not be considered (last six months)
cut_results = []
if not args['nocut']:
    print('Downloading recent preprints...', end='', flush=True)
    cut_results = http_json_as_dict(url2)
    print('%d loaded.' % len(cut_results), flush=True)
    
    # Convert to list of just ids
    cut_results = [int(entry['id']) for entry in cut_results]


# If all results would be cut, there is no point to show more
if len(cut_results) == len(preliminary_results):
    print("All preprints would be cut. Exiting.")
    exit(0)

print("%d preprints for ChemRxiv in total, %d will be cut." %
      (len(preliminary_results), len(cut_results)))

# Create a list of dictionaries (article_id, title, views, downloads, publishing date, days since publishing,
# downloads/days) with only the papers that are left; ask statistics for views and downloads
results = []
for index, entry in enumerate(preliminary_results):
    print("Downloading data for preprint %d of %d" % (index + 1, len(preliminary_results)), end='\r')

    # Add entry if id is not in cut_results!
    if entry['id'] not in cut_results:
        data = {'id': int(entry['id']),
                'title': entry['title'],
                'views': int(http_json_as_dict('https://stats.figshare.com/total/views/article/' +
                                               str(entry['id']))['totals']),
                'downloads': int(http_json_as_dict('https://stats.figshare.com/total/downloads/article/' +
                                               str(entry['id']))['totals']),
                'date': entry['published_date'][0:10],
                'days_online': 0,
                'downloads_per_day': 0.0}
        results.append(data)

print("")


for index, entry in enumerate(results):
    year, month, day = entry['date'].split('-')
    days_online = (datetime.date.today() - datetime.date(int(year), int(month), int(day))).days
    results[index]['days_online'] = int(days_online)
    if days_online > 0:
        results[index]['downloads_per_day'] = float(float(entry['downloads'])/float(days_online))


print("Cleaned data has %d entries." % (len(results)))

# Sort by downloads
results = sorted(results, key=lambda entry: entry['downloads_per_day'])

print("")
print(tabulate.tabulate(results)) #.encode("ascii", "replace"))

