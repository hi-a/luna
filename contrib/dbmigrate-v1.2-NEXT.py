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
import uuid
import os
from platform import linux_distribution
from luna.utils.helpers import get_con_options
from luna.config import db_name

log = logging.getLogger(__file__)
log.info('Luna migration script to db NEXT')

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


def migrate_osimage(json):
    from luna import Cluster

    # nothing to change
    if 'osfamily' in json:
        log.warning('Do not need to migrate {}'.format(json['name']))
        return False

    cluster = Cluster()

    if not cluster:
        raise RuntimeError

    real_root = os.open("/", os.O_RDONLY)
    os.chroot(json['path'])
    dist = linux_distribution(supported_dists=('debian', 'redhat'),
                              full_distribution_name=0)
    os.fchdir(real_root)
    os.chroot(".")
    os.close(real_root)

    json['osfamily'] = dist[0]

    return json


modify_objects(mdb, 'osimage', migrate_osimage)
