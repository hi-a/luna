from ming import create_datastore
import unittest

import os
import luna
import getpass
from helper_utils import Sandbox


expected = {'name': 'general',
            'nodeprefix': 'node',
            'nodedigits': 3,
            'user': getpass.getuser(),
            'path': '',
            'debug': '0',
            'cluster_ips': None,
            'frontend_address': '127.0.0.1',
            'frontend_port': '7050',
            'frontend_https': False,
            'lweb_port': '7051',
            'tracker_interval': '10',
            'tracker_min_interval': '5',
            'tracker_maxpeers': '200',
            'torrent_listen_port_min': '7052',
            'torrent_listen_port_max': '7200',
            'torrent_soft_timeout': '600',
            'torrent_hard_timeout': '3600',
            'ltorrent_pidfile': '/run/luna/ltorrent.pid',
            'lweb_pidfile': '/run/luna/lweb.pid',
            'lweb_workers': '0',
            'named_include_file': '/etc/named.luna.zones',
            'named_zone_dir': '/var/named',
            'dhcp_net': None,
            'dhcp_range_start': None,
            'dhcp_range_end': None,
            'comment': None}


class ClusterUtilsTests(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        print

        self.sandbox = Sandbox()
        self.db = self.sandbox.db
        self.path = self.sandbox.path

        self.cluster = luna.Cluster(mongo_db=self.db, create=True,
                                    path=self.path, user=getpass.getuser())

    @classmethod
    def tearDownClass(self):
        self.sandbox.cleanup()


class ClusterReadTests(unittest.TestCase):

    def setUp(self):

        print

        self.sandbox = Sandbox()
        self.db = self.sandbox.db
        self.path = self.sandbox.path

    def tearDown(self):
        self.sandbox.cleanup()

    def test_read_non_existing_cluster(self):
        self.assertRaises(RuntimeError, luna.Cluster, mongo_db=self.db)

    def test_cluster_read(self):
        luna.Cluster(mongo_db=self.db, create=True)

        cluster = luna.Cluster(mongo_db=self.db)
        expected['path'] = self.path

        for attr in expected:
            self.assertEqual(cluster._json[attr], expected[attr])


class ClusterCreateTests(unittest.TestCase):

    def setUp(self):

        print

        self.sandbox = Sandbox()
        self.db = self.sandbox.db
        self.path = self.sandbox.path

    def tearDown(self):
        self.sandbox.cleanup()

    def test_init_cluster_with_defaults(self):
        cluster = luna.Cluster(mongo_db=self.db, create=True)

        expected['path'] = self.path

        for attr in expected:
            self.assertEqual(cluster._json[attr], expected[attr])

if __name__ == '__main__':
    unittest.main()
