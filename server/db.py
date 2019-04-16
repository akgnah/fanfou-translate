#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import redis
import sqlite3
import pickledb
from threading import Thread
from utils import Queue, iterbetter

DEBUG = True
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if not os.path.exists(os.path.join(BASE_DIR, 'data')):
    os.mkdir(os.path.join(BASE_DIR, 'data'))

cache = pickledb.load(os.path.join(BASE_DIR, 'data/cache.json'), True)
dealt = pickledb.load(os.path.join(BASE_DIR, 'data/dealt.json'), True)
rdb = redis.StrictRedis('10.0.0.13', password='raspberry512', db=2)

class DB(Thread):
    def __init__(self, dbn=':memory:', debug=False):
        Thread.__init__(self)
        self.dbn = dbn
        self.reqs = Queue()
        self.debug = debug
        self.daemon = True
        self.start()

    def run(self):
        self.con = sqlite3.connect(self.dbn, check_same_thread=False)
        self.cur = self.con.cursor()

        while True:
            req, arg, res, many = self.reqs.get()
            if req == '--close--':
                break
            if req == '--commit--':
                self.con.commit()

            try:
                if many:
                    self.cur.executemany(req, arg)
                else:
                    self.cur.execute(req, arg)
            except Exception as ex:
                if self.debug:
                    print(ex)
                self.con.rollback()

            if self.cur.description:
                for row in self.cur:
                    res.put(row)
            else:
                res.put(self.cur.rowcount)
            res.put('--no more--')

        self.con.close()

    def execute(self, req, arg=tuple(), many=False):
        res = Queue()
        self.reqs.put((req, arg, res, many))

    def executemany(self, req, arg=tuple(), many=True):
        res = Queue()
        self.reqs.put((req, arg, res, many))

    def query(self, req, arg=tuple(), many=False):
        res = Queue()
        self.reqs.put((req, arg, res, many))

        def iterwrapper():
            while True:
                row = res.get()
                if row == '--no more--':
                    break
                yield row

        return iterbetter(iterwrapper())

    def close(self):
        self.execute('--close--')

    def commit(self):
        self.execute('--commit--')


class Dict(DB):
    def __init__(self, source='youdao', debug=DEBUG):
        DB.__init__(self, os.path.join(BASE_DIR, 'data/dict.db'), debug=debug)
        self.table = source
        self.execute("CREATE TABLE {} (word BLOB PRIMARYKEY UNIQUE, pho TEXT, trans TEXT, hyphen BLOB)".format(self.table))
        self.commit()

    def insert(self, word, pho, trans, hyphen):
        self.execute("INSERT INTO {} (word, pho, trans, hyphen) VALUES (?, ?, ?, ?)".format(self.table), (word, pho, trans, hyphen))
        self.commit()

    def select(self, word):
        res = self.query("SELECT word, pho, trans, hyphen FROM {} WHERE word = ?".format(self.table), (word,))
        return res.first()


services = {'bing': Dict('bing'), 'youdao': Dict('youdao'), 'iciba': Dict('iciba')}


class User(DB):
    def __init__(self, debug=DEBUG):
        DB.__init__(self, os.path.join(BASE_DIR, 'data/user.db'), debug=debug)
        self.execute("CREATE TABLE user (unique_id BLOB PRIMARYKEY UNIQUE, screen_name BLOB, ssid BLOB, at BLOB)")
        self.commit()

    def insert(self, unique_id, screen_name, ssid, at):
        self.execute("INSERT INTO user (unique_id, screen_name, ssid, at) VALUES (?, ?, ?, ?)", (unique_id, screen_name, ssid, at))
        self.commit()

    def update(self, unique_id, screen_name, ssid, at):
        self.execute("UPDATE user SET screen_name = ?, ssid = ?, at = ? WHERE unique_id = ?", (screen_name, ssid, at, unique_id))
        self.commit()

    def select_ssid(self, ssid):
        res = self.query("SELECT unique_id, screen_name, ssid, at FROM user WHERE ssid = ?", (ssid,))
        return res.first()

    def select(self, unique_id):
        res = self.query("SELECT unique_id, screen_name, ssid, at FROM user WHERE unique_id = ?", (unique_id,))
        return res.first()

    def fetchall(self):
        res = self.query("SELECT unique_id, screen_name, ssid, at FROM user")
        return res.list()


class Push(DB):
    def __init__(self, debug=DEBUG):
        DB.__init__(self, os.path.join(BASE_DIR, 'data/push.db'), debug=debug)
        self.execute("CREATE TABLE push (unique_id BLOB, word BLOB, source BLOB, at BLOB, UNIQUE(unique_id, word, at))")
        self.commit()

    def insert(self, unique_id, word, source, at):
        self.execute("INSERT INTO push (unique_id, word, source, at) VALUES (?, ?, ?, ?)", (unique_id, word, source, at))
        self.commit()

    def fetch(self, at):
        res = self.query("SELECT unique_id, word, source FROM push WHERE at = ?", (at,))
        return res.list()


user = User()
push = Push()