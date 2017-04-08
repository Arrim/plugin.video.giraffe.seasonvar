# coding: utf-8

#
# Copyright © 2017 weirdgiraffe <giraffe@cyberzoo.xyz>
#
# Distributed under terms of the MIT license.
#
from __future__ import unicode_literals
import json
import os
import pytest
import re
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


def memoize(f):
    """ Memoization decorator for a function taking a single argument """
    class memodict(dict):
        def __missing__(self, key):
            ret = self[key] = f(key)
            return ret
    return memodict().__getitem__


@memoize
def file_content(path):
    with open(path, 'rb') as inputf:
        return inputf.read().decode('utf-8')


class RequestsMockResult:
    def __init__(self, path, status_code):
        self.text = file_content(path)
        self.status_code = status_code

    def json(self):
        return json.loads(self.text)


class RequestsMock:
    def __init__(self):
        print()
        methods = ['GET', 'POST']
        self.responses = {}
        self.counters = {}
        for m in methods:
            self.responses[m] = []
            self.counters[m] = 0

    def respond(self, url_regexp, relpath, code=200, methods=['GET']):
        thisdir = os.path.dirname(__file__)
        path = os.path.join(thisdir, relpath)
        for m in methods:
            self.responses[m] += [(re.compile(url_regexp), path, code)]

    def get(self, fullurl, *args, **kwargs):
        o = urlparse(fullurl)
        url = o.scheme + "://" + o.netloc + o.path
        for regexp, path, status in self.responses['GET']:
            if regexp.search(url):
                print('mock for url:{0} - {1}'.format(url, path))
                return RequestsMockResult(path, status)
        pytest.fail("unexpected HTTP GET url:{0} args: {1} kwargs:{2}".format(
            url, args, kwargs))

    def post(self, url, *args, **kwargs):
        for regexp, path, status in self.responses['POST']:
            if regexp.search(url):
                print('mock for url:{0} - {1}'.format(url, path))
                return RequestsMockResult(path, status)
        pytest.fail("unexpected HTTP POST url:{0} args: {1} kwargs:{2}".format(
            url, args, kwargs))


@pytest.fixture()
def requests_mock(monkeypatch):
    mock = RequestsMock()
    monkeypatch.setattr('requests.Session.get', mock.get)
    monkeypatch.setattr('requests.Session.post', mock.post)
    monkeypatch.setattr('requests.get', mock.get)
    monkeypatch.setattr('requests.post', mock.post)
    return mock
