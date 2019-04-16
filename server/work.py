#!/usr/bin/python
# -*- coding: utf-8 -*-
import db
import time
import random
import string
import account
import threading
from datetime import datetime
from json import loads, dumps
from utils import now
# pylint: disable=maybe-no-member


class User:
    def gen_ssid(self, size=12):
        chars = string.digits + string.ascii_letters
        chars = [random.choice(chars) for i in range(size)]
        return ''.join(chars)

    def check(self):
        data = account.main.account.notification({'mode': 'lite'}).json()
        count = 60 if data['mentions'] > 20 else 20
        pages = int(data['mentions'] / count) + 2
        for page in range(1, pages):
            body = {'count': count, 'page': page, 'mode': 'lite'}
            for item in account.main.statuses.mentions(body).json():
                if db.dealt.get(item['id']):
                    continue
                if item['text'].startswith('@饭译 at '):
                    self.deal(item)
                if item['text'].strip() == '@饭译 --renew':
                    self.renew(item)
            time.sleep(0.5)

    def deal(self, item):
        try:
            unique_id = item['user']['unique_id']
            at = datetime.strptime(item['text'][6:].strip(), '%H:%M').strftime('%H:%M')
            if db.user.select(unique_id):
                unique_id, screen_name, ssid, _ = db.user.select(unique_id)
                db.user.update(unique_id, screen_name, ssid, at)
                db.dealt.set(item['id'], 1)
            else:
                ssid = self.gen_ssid()
                screen_name = item['user']['screen_name']
                db.user.insert(unique_id, screen_name, ssid, at)
                self.reply(item, ssid)
        except Exception:
            pass

    def renew(self, item):
        try:
            unique_id = item['user']['unique_id']
            unique_id, screen_name, ssid, at = db.user.select(unique_id)
            ssid = self.gen_ssid()
            db.user.update(unique_id, screen_name, ssid, at)
            self.reply(item, ssid)
        except Exception:
            pass

    def reply(self, item, ssid):
        try:
            unique_id = item['user']['unique_id']
            body = {'user': unique_id, 'text': ssid, 'mode': 'lite'}
            account.main.direct_messages.new(body)
            db.dealt.set(item['id'], 1)
        except Exception:
            pass

    def update(self):
        for unique_id, screen_name, ssid, at in db.user.fetchall():
            body = {'id': unique_id, 'mode': 'lite'}
            screen_name = account.vice.users.show(body).json()['screen_name']
            db.user.update(unique_id, screen_name, ssid, at)
            time.sleep(2.0)


class Push:
    def check(self):
        at = datetime.strftime(now(), '%Y/%m/%d %H:%M')
        for unique_id, word, source in db.push.fetch(at):
            screen_name = db.user.select(unique_id)[1]
            word, pho, trans, _ = db.services[source].select(word)
            if pho:
                text = '@{} {} [{}] {}'.format(screen_name, word, pho, trans)
            else:
                text = '@{} {} {}'.format(screen_name, word, trans)
            result = {'status': text, 'in_reply_to_user_id': unique_id}
            db.rdb.lpush('fanyi.push', dumps(result))

    def send(self):
        if db.rdb.llen('fanyi.push'):
            result = loads(db.rdb.rpop('fanyi.push'))
            account.main.statuses.update(result)

    def public(self):
        if db.rdb.scard('fanyi.public'):
            word, pho, trans = loads(db.rdb.spop('fanyi.public'))
            if pho:
                text = '{} [{}] {}'.format(word, pho, trans)
            else:
                text = '{} {}'.format(word, trans)
            account.vice.statuses.update({'status': text})


user = User()
push = Push()


def user_check():
    while True:
        try:
            user.check()
        except Exception as ex:
            print(ex)
        time.sleep(180)


def user_update():
    while True:
        try:
            if now().hour == 4 and now().minute < 5:
                user.update()
        except Exception as ex:
            print(ex)
        time.sleep(300)


def push_check():
    while True:
        try:
            push.check()
        except Exception as ex:
            print(ex)
        time.sleep(60.1 - now().second)


def push_send():
    while True:
        try:
            push.send()
        except Exception as ex:
            print(ex)
        time.sleep(5)


def push_public():
    while True:
        try:
            if now().minute % 5 == 0:
                push.public()
        except Exception as ex:
            print(ex)
        time.sleep(60.1 - now().second)


if __name__ == '__main__':
    threads = []

    for func in (user_check, user_update, push_check, push_send, push_public):
        threads.append(threading.Thread(target=func))

    for t in threads:
        t.daemon = True
        t.start()

    for t in threads:
        t.join()