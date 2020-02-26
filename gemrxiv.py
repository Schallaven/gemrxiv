#!/usr/bin/env python2

# gemRxiv
# Copyright (C) 2018 by Sven Kochmann
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

import urllib2
import json
import datetime
import tabulate

def http_json_as_dict(url):
    return json.load(urllib2.urlopen(url))


# According to Figshare API page_size=1000 is the maximum and item_type = 12 are pre-prints;
# All chemRxiv pre-prints have group = 13668
preliminary_results = http_json_as_dict('https://api.figshare.com/v2/articles?'
                            'group=13668&page_size=1000'
                            '&order=published_date&order_direction=desc')

# These results will not be considered (last six months)
cut_results = http_json_as_dict('https://api.figshare.com/v2/articles?'
                                     'group=13668&page_size=1000&published_since=2019-12-01'
                                     '&order=published_date&order_direction=desc')

# Convert to list of just ids
cut_results = [int(entry['id']) for entry in cut_results]

print("%d results for ChemRxiv in total, %d will be cut." %
      (len(preliminary_results), len(cut_results)))

# Create a list of dictionaries (article_id, title, views, downloads, publishing date, days since publishing,
# downloads/days) with only the papers that are left; ask statistics for views and downloads
results = [{'id': int(entry['id']),
            'title': entry['title'],
            'views': int(http_json_as_dict('https://stats.figshare.com/total/views/article/' +
                                            str(entry['id']))['totals']),
            'downloads': int(http_json_as_dict('https://stats.figshare.com/total/downloads/article/' +
                                            str(entry['id']))['totals']),
            'date': entry['published_date'][0:10],
            'days_online': 0,
            'downloads_per_day': 0.0}
           for entry in preliminary_results if entry['id'] not in cut_results]

for index, entry in enumerate(results):
    year, month, day = entry['date'].split('-')
    days_online = (datetime.date.today() - datetime.date(int(year), int(month), int(day))).days
    results[index]['days_online'] = int(days_online)
    results[index]['downloads_per_day'] = float(float(entry['downloads'])/float(days_online))

print("Cleaned data has %d entries." % (len(results)))

# Sort by downloads
results = sorted(results, key=lambda entry: entry['downloads_per_day'])

print("\n")
print(tabulate.tabulate(results).encode("ascii", "replace"))

