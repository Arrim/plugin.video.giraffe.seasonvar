#!/usr/bin/env python
# coding: utf-8
# vim:fenc=utf-8:sts=0:ts=4:sw=4:et:tw=80

#
# Copyright © 2016 gr4ph3 <giraffeoncode@gmail.com>
#
# Distributed under terms of the MIT license.
#
import requests
import logging
try:
    from urllib.parse import urljoin
except ImportError:
    from urllib import urljoin


BASEURL = 'http://seasonvar.ru'


logger = logging.getLogger(__name__)


class NetworkError(Exception):
    """exception which occures on any kind of network error
    i.e. not able to connect, not able to resolve, etc."""
    pass


class HTTPError(Exception):
    """exception which occures on any kind of http not 200 codes"""
    pass


class Requester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 7_0 like Mac OS X) '
                          'AppleWebKit/537.51.1 (KHTML, like Gecko) '
                          'Version/7.0 Mobile/11A465 Safari/9537.53',
        })

    def _get(self, url=None, **custom_headers):
        try:
            page = self.session.get(url, headers=custom_headers)
            if page.status_code == 200:
                page.encoding = 'utf-8'
                return page
            else:
                raise HTTPError(
                    'bad GET page response for url {0}\n{1}'.format(url, page)
                    )
        except requests.exceptions.RequestException as e:
            raise NetworkError(repr(e))

    def get(self, url=None, **custom_headers):
        try:
            page = self.session.get(url, headers=custom_headers)
            if page.status_code == 200:
                page.encoding = 'utf-8'
                return page.text
            else:
                raise HTTPError(
                    'bad GET page response for url {0}\n{1}'.format(url, page)
                    )
        except requests.exceptions.RequestException as e:
            raise NetworkError(repr(e))

    def get_json(self, url=None, **custom_headers):
        page = self._get(url, **custom_headers)
        return page.json()


class SeasonvarRequester(Requester):
    def __init__(self):
        super(SeasonvarRequester, self).__init__()
        self.session.headers.update({
            'Host': 'seasonvar.ru',
            'Accept-Language': 'ru-RU',
            'Origin': 'http://seasonvar.ru',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, sdch'
        })
        self.session.cookies.update({
            'IIIIIIIIIIIIIIIII': 'WerTylv_tr',
            'sva': 'lVe324PqsI24',
            'html5default': '1'
            })

    def absurl(self, relurl):
        return urljoin('http://seasonvar.ru', relurl)
