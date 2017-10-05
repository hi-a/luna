#!/usr/bin/env python
'''
Written by Dmitry Chirikov <dmitry@chirikov.ru>
This file is part of Luna, cluster provisioning tool
https://github.com/dchirikov/luna

This file is part of Luna.

Luna is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Luna is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Luna.  If not, see <http://www.gnu.org/licenses/>.

'''

import logging
import pymongo
from luna.utils.helpers import get_con_options
from luna.config import db_name

log = logging.getLogger(__file__)
log.info('Luna migration script from db v1.2 to db v1.3')

try:
    mclient = pymongo.MongoClient(**get_con_options())
    mdb = mclient[db_name]
except:
    log.error("Unable to connect to MongoDB.")
    raise RuntimeError


def modify_objects(mdb, collection=None, fun=None):

    if not (collection and fun):
        log.error('collection and fun need to be specified')
        return False

    log.info('Migrating collection {}'.format(collection))

    mongo_collection = mdb[collection]

    objects = mongo_collection.find()
    new_jsons = []

    for json in objects:
        new_json = fun(json)
        if new_json:
            new_jsons.append(new_json)

    for json in new_jsons:

        log.info('Converting {}'.format(json['name']))

        mongo_collection.update(
            {'_id': json['_id']},
            json,
            multi=False, upsert=False
        )


def migrate_cluster(json):

    # Not the correct migration script
    if 'db_version' not in json:
        log.warning('You need to run the v1.2 migration script first')
        return False

    # nothing to change
    if json['db_version'] != 1.2:
        log.warning('This script is not needed or has already been run')
        return False

    json['db_version'] = 1.3
    json.pop('user')
    json.pop('path')
    json.pop('lweb_pidfile')
    json.pop('lweb_num_proc')
    json.pop('torrent_pidfile')
    json.pop('torrent_listen_port_min')
    json.pop('torrent_listen_port_max')
    json.pop('tracker_interval')
    json.pop('tracker_maxpeers')
    json.pop('tracker_min_interval')
    json.pop('named_include_file')
    json.pop('named_zone_dir')

    return json


modify_objects(mdb, 'cluster', migrate_cluster)
