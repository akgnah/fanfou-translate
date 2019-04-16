#!/usr/bin/python
# -*- coding: utf-8 -*
import db
import re
import uuid
from json import dumps
from datetime import datetime
from flask import Flask, request, make_response
from utils import tomorrow
from translate import Client

app = Flask(__name__)


@app.route('/')
def index():
    return 'hello, world'


@app.route('/fanyi')
def api_fanyi():
    ssid = request.args.get('ssid', 'public')
    word = request.args.get('word', 'hello')
    source = request.args.get('source', 'youdao')
    client = Client(source)

    word, pho, trans, hyphen = client.translate(word)

    if re.match(r"^[a-zA-Z-'\.\s]+$", word) and trans != '404 Not Found':
        try:
            unique_id, _, _, at = db.user.select_ssid(ssid)
            at = '{} {}'.format(datetime.strftime(tomorrow(), '%Y/%m/%d'), at)
            db.push.insert(unique_id, word, source, at)
        except Exception:  # public or invalid ssid
            db.rdb.sadd('fanyi.public', dumps([word, pho, trans]))

    result = dumps({'word': word, 'pho': pho, 'trans': trans, 'hyphen': hyphen})
    resp = make_response(result)
    resp.headers['Content-Type'] = 'application/json'
    resp.headers['Access-Control-Allow-Origin'] = '*'

    return resp


if __name__ == '__main__':
    app.run(port=5000)