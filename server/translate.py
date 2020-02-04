#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re
import db
import time
import requests
from utils import to_unicode
from bs4 import BeautifulSoup
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


def fetch(url, host, allow_redirects=True, timeout=100):
    s = requests.Session()
    headers = {
        'Host': host,
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
    }
    s.headers.update(headers)

    return s.get(url, allow_redirects=allow_redirects, timeout=timeout)


def bing(word):
    try:
        url = 'http://cn.bing.com/dict/SerpHoverTrans?q=%s' % word
        resp = fetch(url, 'cn.bing.com')
        text = resp.text
    except Exception:
        return None

    if resp.status_code == 200 and text:
        soup = BeautifulSoup(text, 'lxml')
        pho = soup.find('span', {'class': 'ht_attr'})
        pho = pho.text[1:-2] if pho else ''
        _word = soup.find('h4').text.strip()
        if _word.lower() != word.lower():
            return None
        trans = []
        for item in soup.find_all('li'):
            transText = item.get_text()
            if transText:
                trans.append(transText)
        return _word, pho, '\n'.join(trans)
    else:
        return None


def youdao(word):
    try:
        url = 'http://dict.youdao.com/fsearch?q=%s&doctype=xml&xmlVersion=3.2' % word
        resp = fetch(url, 'dict.youdao.com')
        text = resp.content
    except Exception:
        return None

    if resp.status_code == 200 and text:
        tree = ET.ElementTree(ET.fromstring(text))
        pho = tree.find('phonetic-symbol')
        pho = tree.find('phonetic-symbol').text if pho != None else ''
        _word = tree.find('return-phrase').text.strip()
        if _word.lower() != word.lower():
            return None
        customTranslation = tree.find('custom-translation')
        if not customTranslation:
            return None
        trans = []
        for t in customTranslation.findall('translation'):
            transText = t[0].text
            if transText:
                trans.append(transText)
        return _word, pho, '\n'.join(trans)
    else:
        return None


def iciba(word):
    try:
        url = 'http://open.iciba.com/huaci_new/dict.php?word=%s' % word
        resp = fetch(url, 'open.iciba.com')
        text = resp.text
    except Exception:
        return None

    if resp.status_code == 200 and text:
        try:
            pattern = r'(<div id=\\\"icIBahyI-title\\\"[^>]+>([^<]+?)</div>)'
            _word = re.search(pattern, text).group(2).strip()
        except Exception:
            _word = word
        if _word.lower() != word.lower():
            return None
        pattern = r'(<div class=\\\"icIBahyI-dictbar\\\">[\s\S]+</div>)'
        text = re.search(pattern, text).group(1).replace('\\"', '"')
        soup = BeautifulSoup(text, 'lxml')
        pho = soup.find('strong', {'lang': 'EN-US'})
        pho = pho.text if pho else ''
        trans = []
        for item in soup.find_all('p'):
            transText = item.get_text()
            transText = re.sub(r'\s+', ' ', transText.replace('\t', '')).strip()
            if transText:
                trans.append(transText)
        if not trans:
            trans = [soup.find('div', {'class': 'icIBahyI-suggest2'}).get_text()]
        return _word, pho, '\n'.join(trans)
    else:
        return None


class Client:
    def __init__(self, service='bing'):
        self.services = {'bing': bing, 'youdao': youdao, 'iciba': iciba}
        self.db = db.services.get(service)
        self.query = self.services.get(service)

    def translate(self, word):
        result = self.db.select(word) or self.db.select(word.lower())
        if result:
            return result

        try:
            word, pho, trans = self.query(word)
        except Exception:
            pho, trans = '', '404 Not Found'
        hyphen = self.hyphenate(word)
        if trans != '404 Not Found' and re.match(r"^[a-zA-Z-'\.\s]+$", word):
            self.db.insert(word, pho, trans, hyphen)

        return word, pho, trans, hyphen

    def hyphenate(self, word):
        if not re.match(r"^[a-zA-Z-'\.\s]+$", word):
            return word

        hyphen = db.cache.get(word)
        if hyphen:
            return hyphen

        try:
            url = 'http://dict.cn/%s' % word
            resp = fetch(url, 'dict.cn', False)
            pattern = to_unicode(r'<h1 class="keyword" tip="音节划分：([^"]+)">')
            hyphen = re.search(pattern, resp.text).group(1).replace('&#183;', '-')
        except Exception:
            hyphen = word
        db.cache.set(word, hyphen)

        return hyphen


if __name__ == "__main__":
    client = Client('youdao')
    print(client.translate('procedure'))
    time.sleep(0.5)