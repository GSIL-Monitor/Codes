# coding=utf-8
__author__ = 'victor'

import os
import sys
reload(sys)
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.setdefaultencoding('utf-8')

import stopword

standard_stops = stopword.get_standard_stopwords()
locations = stopword.get_stopwords('location')
search_names = stopword.get_stopwords('search')


def filter_1char(seq):

    return filter(lambda x: len(x) > 1, seq)


def filter_digits(seq):

    return filter(lambda x: not str(x).isdigit(), seq)


def filter_stops(seq):

    global standard_stops
    return filter(lambda x: x not in standard_stops, seq)


def filter_locations(seq):

    global locations
    return filter(lambda x: x not in locations, seq)


def filter_search_names(seq):

    global search_names
    return filter(lambda x: x not in search_names, seq)


def get_filter(*filter_names):

    filter_names = set(filter_names)
    filters = []
    if '1char' in filter_names:
        filters.append(filter_1char)
    if 'digit' in filter_names:
        filters.append(filter_digits)
    if 'location' in filter_names:
        filters.append(filter_locations)
    if 'stopword' in filter_names:
        filters.append(filter_stops)
    if 'search' in filter_names:
        filters.append(filter_search_names)

    def filter_combined(seq):

        for f in filters:
            seq = f(seq)

        return seq

    return filter_combined


def get_default_filter():

    return get_filter('1char', 'digit', 'stopword', 'location')


def get_search_name_filter():

    return get_filter('search', 'location')


if __name__ == '__main__':

    f = get_filter('1char', 'digit')
    print f([u'2015', u'年', u'毛主次', u'傻逼'])