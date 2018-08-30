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

import urllib
import urllib2
import copy
import socket
import jieba
import jieba.posseg as pseg
jieba.load_userdict(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dict.txt'))
from LTML import LTML


class Tagger(object):

    ltp_url = u'http://ltpapi.voicecloud.cn/analysis/?'

    data = {
        'api_key': '41j8c6KG7RjtyMBERo5EkPiszrUEzlPwwG8UHarc',
        'format': 'plain',
        'pattern': 'pos'
    }

    def __init__(self, name='jieba', **kwargs):

        self.name = name
        self.kwargs = dict(kwargs)

        self.__add_names()

    def __add_names(self):

        if self.kwargs.get('cnames', False):
            if self.name == 'jieba':
                db = dbcon.connect_torndb()
                for company in db.query('select company.name from company, company_scores '
                                        'where company_scores.companyId=company.id and company_scores>0.2 '
                                        'and char_length(company.name)<7;'):
                    jieba.add_word(company.name, tag='cn')
                db.close()

        if self.kwargs.get('tags', False):
            if self.name == 'jieba':
                db = dbcon.connect_torndb()
                for tag in db.query('select name from tag where type in (11011, 11012, 11013, 11050, 11051, '
                                    '11052, 11053, 11054, 11100);'):
                    if not is_engish_word(tag.name):
                        jieba.add_word(tag.name.lower(), tag='itag')
                for tag in db.query('select name from tag where type=11010;'):
                    if not is_engish_word(tag.name):
                        jieba.add_word(tag.name.lower(), tag='tag')
                db.close()

        if self.kwargs.get('itags', False):
            if self.name == 'jieba':
                db = dbcon.connect_torndb()
                for tag in db.query('select name from tag where type in (11011, 11012, 11013, 11014);'):
                    if not is_engish_word(tag.name):
                        jieba.add_word(tag.name.lower(), tag='itag')
                db.close()

    def add_word(self, word, freq=None, tag=None):

        jieba.add_word(word, freq=freq, tag=tag)

    def tag(self, inp, seged=False):

        """
        pos tag
        :param input: a sentence or a sequence
        :param seged: whether input is segmented, default is True
        :return: (words sequence, tag sequence)
        """
        return{
            'jieba': self.tag_jieba,
            'ltp': self.tag_ltp
        }[self.name](inp, seged)

    def tag_jieba(self, inp, seged):

        if seged:
            inp = ' '.join(inp)
        for r in pseg.cut(inp):
            yield (r.word, r.flag)

    def tag_ltp(self, inp, seged):

        """
        pos tag using ltp, size of inp should be limited to lower than 10k
        :param inp:
        :param seged:
        :return:
        """

        params = copy.copy(self.data)
        socket.setdefaulttimeout(10)

        if seged:
            inp = map(lambda x: unicode(x).encode('utf-8'), inp)
            ltml = LTML()
            ltml.build_from_words(inp)
            params.update({
                'text': ltml.tostring(),
                'xml_input': 'true'
            })

        else:
            inp = inp.encode('utf-8') if isinstance(inp, unicode) else inp
            params.update({
                'text': urllib.quote(inp)
            })

        params = urllib.urlencode(params)
        try:
            request = urllib2.Request(self.ltp_url)
            content = urllib2.urlopen(request, params).read().strip()
            for r in content.split():
                yield r.split('_')[0].decode('utf-8'), r.split('_')[1]
        except socket.timeout:
            print 'time out'
        except Exception, e:
            print inp
            print e


if __name__ == '__main__':

    print 'main', __file__

    t = Tagger(tags=True)
    for w in t.tag(u'基因编辑SaaS工具'):
        print w[0], w[1]