# coding=utf-8
__author__ = 'victor'

import os
import sys
reload(sys)
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.setdefaultencoding('utf-8')

import db as dbcon
from functions import is_engish_word

import codecs
import urllib2
import os
import jieba
jieba.load_userdict(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dict.txt'))
import hants


class Segmenter(object):

    ltp_url = u'http://ltpapi.voicecloud.cn/analysis/?' \
              u'api_key=41j8c6KG7RjtyMBERo5EkPiszrUEzlPwwG8UHarc&' \
              u'text=%s&' \
              u'format=plain&' \
              u'pattern=ws'

    def __init__(self, name='jieba', **kwargs):

        self.name = name
        self.opts = dict(kwargs)

        self.__add_tags()

    def __add_tags(self):

        if self.opts.get('tag', True):
            if self.name == 'jieba':
                db = dbcon.connect_torndb()
                for tag in db.query('select distinct name from tag where type>11009 and type<11500;'):
                    if not tag or not tag.name:
                        continue
                    jieba.add_word(tag.name, tag='tag')
                db.close()

        if self.opts.get('itags', False):
            if self.name == 'jieba':
                db = dbcon.connect_torndb()
                for tag in db.query('select name from tag where type in (11011, 11012, 11013, 11014);'):
                    if not is_engish_word(tag.name):
                        jieba.add_word(tag.name.lower(), tag='itag')
                db.close()

    def add_dict(self, name):

        path = os.path.join(os.path.split(os.path.realpath(__file__))[0], '../dict/%s' % name)
        if os.path.exists(path):
            for line in codecs.open(path, encoding='utf-8'):
                jieba.add_word(line.strip(), tag=name)

    def add_word(self, word, freq=None, tag=None):

        jieba.add_word(word, freq=freq, tag=tag)

    def cut(self, sentence):

        if not (isinstance(sentence, str) or isinstance(sentence, unicode)):
            return ''
        sentence = hants.translate(sentence)
        return {
            'jieba': self.cut_jieba,
            'ltp': self.cut_ltp
        }[self.name](sentence)

    def cut4search(self, sentence):

        return jieba.cut_for_search(hants.translate(sentence))

    def cut_jieba(self, sentence):

        return jieba.cut(sentence)

    def cut_ltp(self, sentence):

        url = self.ltp_url % sentence.replace('\n', '')
        # print url
        try:
            response = urllib2.urlopen(url)
            return response.read().strip().split()
        except Exception, e:
            raise e

    def cut_pull(self, sentence):

        pass


if __name__ == '__main__':

    print 'main'
    s = Segmenter('jieba')
    for x in s.cut(u'移动互联网是趋势'):
        print x