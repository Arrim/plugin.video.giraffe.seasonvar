# coding: utf-8

#
# Copyright © 2017 weirdgiraffe <giraffe@cyberzoo.xyz>
#
# Distributed under terms of the MIT license.
#
from kodi import logger, Plugin
import seasonvar
from datetime import datetime, timedelta


def week(plugin):
    date = datetime.today()
    for date_offset in range(7):
        datestr = date.strftime('%d.%m.%Y')
        dayurl = plugin.make_url({
            'screen': 'day',
            'date': datestr,
        })
        plugin.add_screen_directory(datestr, dayurl)
        date -= timedelta(days=1)
    searchurl = plugin.make_url({'screen': 'search'})
    plugin.add_screen_directory('[COLOR FFFFD700]поиск[/COLOR]', searchurl)
    plugin.publish_screen(True)


def day(plugin):
    date = plugin.args.get('date')
    if date is None:
        logger.error('{0}: "date" arg is missing or malformed: {0}'.format(
            'screen "day"', plugin.args))
        plugin.publish_screen(False)
        return
    for i in seasonvar.day_items(date):
        url = plugin.make_url({
            'screen': 'episodes',
            'url': i['url'],
        })
        name = '{0} [COLOR FFFFD700]{1}[/COLOR]'.format(
                i['name'], i['changes'])
        plugin.add_screen_directory(name, url)
    plugin.publish_screen(True)


def episodes(plugin):
    season_url = plugin.args.get('url')
    if season_url is None:
        logger.error('{0}: "url" arg is missing or malformed: {0}'.format(
            'screen "episodes"', plugin.args))
        plugin.publish_screen(False)
        return
    tr = plugin.args.get('tr')
    season = seasonvar.season_info(season_url)
    if season is None:
        logger.error('{0}: failed to get season info: {0}'.format(
            'screen "episodes"', plugin.args))
        plugin.publish_screen(False)
        return
    if season['total'] > 1:
        url = plugin.make_url({
            'screen': 'seasons',
            'url': season_url,
        })
        name = '[COLOR FFFFD700]сезон[/COLOR]: {0} / {1}'.format(
                season['number'], season['total'])
        plugin.add_screen_directory(name, url)
    if len(season['playlist']) > 1:
        url = plugin.make_url({
            'screen': 'translations',
            'url': season_url,
            'tr': tr,
        })
        name = '[COLOR FFFFD700]озвучка[/COLOR]: {0}'.format(
                tr if tr is not None else 'Стандартная')
        plugin.add_screen_directory(name, url)
    pl_url = (x['url'] for x in season['playlist'] if x['tr'] == tr)
    for e in (x for url in pl_url for x in seasonvar.episodes(url)):
        url = plugin.make_url({'play': e['url']})
        plugin.add_screen_item(e['name'], url)
    plugin.publish_screen(True, True)


def seasons(plugin):
    season_url = plugin.args.get('url')
    if season_url is None:
        logger.error('{0}: "url" arg is missing or malformed: {0}'.format(
            'screen "seasons"', plugin.args))
        plugin.publish_screen(False)
        return
    num, seasons = seasonvar.seasons(season_url)
    if seasons is None:
        logger.error('{0}: failed to get season info: {0}'.format(
            'screen "seasons"', plugin.args))
        plugin.publish_screen(False)
        return
    for n, s in enumerate(seasons, 1):
        prefix = '* ' if n == num else ''
        name = '{0}сезон {1}'.format(prefix, n)
        url = plugin.make_url({
            'screen': 'episodes',
            'url': s,
        })
        plugin.add_screen_directory(name, url)
    plugin.publish_screen(True, True)


def translations(plugin):
    season_url = plugin.args.get('url')
    if season_url is None:
        logger.error('{0}: "url" arg is missing or malformed: {0}'.format(
            'screen "translations"', plugin.args))
        plugin.publish_screen(False)
        return
    tr = plugin.args.get('tr')
    season = seasonvar.season_info(season_url)
    if season is None:
        logger.error('{0}: failed to get season info: {0}'.format(
            'screen "translations"', plugin.args))
        plugin.publish_screen(False)
        return
    for n, pl in enumerate(season['playlist']):
        if tr is None and n == 0 or pl['tr'] == tr:
            prefix = '* '
        else:
            prefix = ''
        url = plugin.make_url({
            'screen': 'episodes',
            'url': season_url,
            'tr': pl['tr'],
        })
        name = '{0}{1}'.format(
                prefix,
                pl['tr'] if pl['tr'] is not None else 'Стандартная')
        plugin.add_screen_directory(name, url)
    plugin.publish_screen(True, True)


def play(plugin):
    play_url = plugin.args.get('url')
    if play_url is None:
        logger.error('{0}: "url" arg is missing or malformed: {0}'.format(
            'play', plugin.args))
        plugin.publish_screen(False)
        return
    plugin.play(play_url)


def render_screen(plugin):
    screen = plugin.args.get('screen')
    try:
        if 'play' in plugin.args:
            play(plugin)
            return

        {'week': week,
         'day': day,
         'episodes': episodes,
         'seasons': seasons,
         'translations': translations,
         }[screen](plugin)
    except KeyError:
        logger.error('unexpected screen "{0}"'.format(screen))
    except seasonvar.NetworkError:
        logger.error('NetworkError')
        plugin.show_notification(
            'Network error',
            'Check your connection')
    except seasonvar.HTTPError:
        logger.error('HTTPError')
        plugin.show_notification(
            'HTTP error',
            'Something goes wrong. Please, send your logs to addon author')


if __name__ == "__main__":
    import sys
    render_screen(Plugin(*sys.argv))
