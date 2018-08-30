# coding=utf-8
__author__ = 'victor'

from zhtools.segment import Segmenter
from zhtools import stopword
from dsutil import SortedFixLenList
import nlpconfig
import re
import torndb
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


normal_nick = re.compile(u'^#*([^#]+)#*$')


class Recognizer(object):

    def __init__(self, docs):

        self.segmenter = Segmenter('jieba')
        self.stopwords = stopword.get_stopwords('chinese', 'english', 'mail', 'code', 'location')
        self.df = self.__build_df(docs)
        self.min_df = 0.01 * len(docs)
        self.tops = self.__get_tops(200)

    def __get_tops(self, n):

        tops = SortedFixLenList(n, key=lambda x: x[1])
        for w, c in self.df.iteritems():
            tops.append((w, c))
        return sorted([x[0] for x in tops], key=lambda x: len(x), reverse=True)

    def __build_df(self, docs):

        df = {}
        for doc in docs:
            doc = set(self.segmenter.cut(doc)) if (isinstance(doc, str) or isinstance(doc, unicode)) else set(doc)
            for word in doc:
                df[word] = df.get(word, 0) + 1
        return df

    def get_short_name(self, full_name, easy=False):

        global normal_nick
        if easy:
            if len(full_name) < 5:
                return full_name
            name = full_name
            for fword in self.tops:
                name = name.replace(fword, '#')
                m = normal_nick.findall(name)
                if m and len(m) == 1 and 1 < len(m[0]) < 5:
                    return m[0]
            m = normal_nick.findall(name)
            if m and len(m) == 1 and float(len(m[0]))/len(full_name) < 0.51:
                return m[0]
            return name.replace('#', '')
        else:
            words = [(i, word) for i, word in enumerate(self.segmenter.cut(full_name)) if word not in self.stopwords]
            for word in words:
                self.df[word[1]] = self.df.get(word[1], 0) + 1
            words = filter(lambda x: self.df.get(x[1]) <= self.min_df and
                                     (not (len(x[1]) > 2 and self.df.get(x[1]) > 5)), words)
            if len(words) == 0:
                print full_name, 'no name here'
                return
            if len(words) == 1:
                return words[0][1]
            else:
                candis, index, couple = [], words[0][0], words[0][1]
                for i in xrange(1, len(words)):
                    if words[i][0]-1 == index:
                        couple += words[i][1]
                    else:
                        candis.append(couple)
                        couple = words[i][1]
                    index = words[i][0]
                candis.append(couple)
                return sorted(candis, key=lambda x: self.df.get(x, 0))[0]


class NickExtractor(Recognizer):

    def __init__(self):

        db = torndb.Connection(**nlpconfig.get_mysql_config_tshbao())
        names = map(lambda x: x.companyFullName, db.query(u'select companyId, companyFullName from company;'))
        db.close()
        Recognizer.__init__(self, names)


if __name__ == '__main__':

    print __file__

    # db = torndb.Connection(**config.get_mysql_config_tshbao())
    # results = db.query(u'select companyId, companyFullName from company;')
    # r = Recognizer(map(lambda x: x.companyFullName, results))
    # print r.get_short_name(u'深圳市龙游云技术有限公司')
    #
    # # for result in results:
    # #     cid, name = result.companyId, r.get_short_name(result.companyFullName)
    # #     if name:
    #         db.execute(u'update company set companyShortName = "%s" '
    #                    u'where companyId = %s' % (name.encode('utf-8'), cid))
    #
    # db.close()

    e = NickExtractor()
    print e.get_short_name(u'山东物流集团', easy=False)