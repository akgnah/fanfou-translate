#!/usr/bin/python
# -*- coding: utf-8 -*-
import fanfou

consumer = {
    'key': 'your API Key',
    'secret': 'your API Secret'
}

main = fanfou.XAuth(consumer, 'username1', 'password1')
fanfou.bound(main)

vice = fanfou.XAuth(consumer, 'username2', 'password2')
fanfou.bound(vice)