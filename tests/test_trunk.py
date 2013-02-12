# -*- coding: utf-8  -*-
import os

from unittest import TestCase

from trunk import Trunk


class TrunkTest(TestCase):
    def setUp(self):
        dsn = os.environ.get("DATABASE_URL")
        self.listener = Trunk(dsn or "postgres://localhost/trunk")
        self.notifier = Trunk(dsn or "postgres://localhost/trunk")

    def test_get(self):
        self.listener.listen("trunk_get")
        self.notifier. notify("trunk_get", "payload")
        channel, payload = self.listener.get("trunk_get")
        self.assertEqual(channel, "trunk_get")
        self.assertEqual(payload, "payload")

    def test_listen(self):
        self.listener.listen("trunk_listen")
        self.assertTrue("trunk_listen" in self.listener.channels())

    def test_unlisten(self):
        self.listener.listen("trunk_channels")
        self.assertTrue("trunk_channels" in self.listener.channels())
        self.listener.unlisten("trunk_channels")
        self.assertTrue("trunk_channels" not in self.listener.channels())

    def tearDown(self):
        self.listener.close()
        self.notifier.close()
