# coding=utf-8
__author__ = 'victor'

import os
import codecs


def get_standard_stopwords():

    standard_list = ['english', 'chinese', 'mail', 'code']
    return get_stopwords(*standard_list)


def get_stopwords(*args):

    stopword_source_dir = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'stopwords_source')
    stopword_sources = os.listdir(stopword_source_dir)
    stopwords = set()
    for arg in args:
        if arg in stopword_sources:
            stopwords.update([line.strip() for line in codecs.open(os.path.join(stopword_source_dir, arg),
                                                                   encoding='utf-8') if line.strip()])
    return stopwords


if __name__ == '__main__':

    print get_standard_stopwords()