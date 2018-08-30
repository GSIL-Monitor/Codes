# coding=utf-8
__author__ = 'wangqc'


import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
from common import dbutil


import logging, codecs, json
from datetime import datetime, timedelta
from collections import defaultdict

# logging
logger_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'logs/tmp.log')
logging.basicConfig(level=logging.INFO, format='%(name)-12s %(asctime)s %(levelname)-8s %(message)s', filename=logger_path)
logger_track = logging.getLogger('track')


class NewAppDominator(object):

    def __init__(self):

        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()
        self.types = ['free', 'charge', 'grossing']
        self.genres = self._get_genres()

    def _get_genres(self):
        genres = [None]
        for line in codecs.open(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../track/files/ios_rank')):
            gid = json.loads(line.strip()).get('id')
            if gid < 7000: genres.append(gid)
        return genres

    def new_dominator(self, today=None, type='free', genre=None):

        today = today or datetime.today()
        one_week_before, three_month_before = today - timedelta(days=8), today - timedelta(days=90)
        dominate_domain = [item['_id'] for item in list(self.mongo.trend.appstore_rank.aggregate([
            {'$match': {'date': {'$gt': one_week_before, '$lte': today}, 'rank': {'$lte': 10}, 'type': type, 'genre': genre}},
            {'$group': {'_id': '$trackId', 'times': {'$sum': 1}}},
            {'$match': {'times': {'$gte': 7}}}]))]

        def never_dominate_before(track_id):

            top_rank = list(self.mongo.trend.appstore_rank.find({'trackId': track_id, 'type': type, 'genre': genre,
                                                        'date': {'$gt': three_month_before, '$lte': one_week_before}}
                                                       ).sort([('rank', 1)]).limit(10))
            return top_rank[-1]['rank'] > 30 if top_rank else True

        new_dominate_domain = filter(never_dominate_before, dominate_domain)
        new_dominator = set()
        for track_id in new_dominate_domain:
            for aid in dbutil.get_artifacts_from_iOS(self.db, track_id):
                cid = dbutil.get_artifact_company(self.db, aid)
                corp_round = dbutil.get_company_round(self.db, cid)
                if corp_round < 1060:
                    app_name = self.db.query('select name from artifact where id = %s' % (aid))[0]['name']
                    company_name = dbutil.get_company_name(self.db, cid)
                    logger_track.info('\nDate: %s Genre: %s Type: %s\nDominator: %s Company: %s\n\n'
                                      % (today, genre, type, app_name, company_name))
                    new_dominator.add((cid, company_name, app_name))
        return new_dominator

    def search(self, _, day_begin, day_end):
        res = defaultdict(set)
        for t in self.types:
            for g in self.genres:
                for d in range(int(day_begin), int(day_end)):
                    date = datetime(2017, 7, 1) + timedelta(days=d)
                    new_dominator = self.new_dominator(date, t, g)
                    if new_dominator: res['%s-%s' % (t, g) ].update(new_dominator)
        with codecs.open('tmp/tmp.txt', 'w', 'utf-8') as fo:
            for k, v in res.items():
                fo.write('%s\n%s\n\n' % (k, '\n'.join([' '.join(map(str, e)) for e in v])))
        return {k: list(v) for k, v in res.items()}


if __name__ == "__main__":
    nad = NewAppDominator()
    #y, m, d = map(int, (sys.argv[1], sys.argv[2], sys.argv[3]))
    #nad.new_dominator(datetime(y, m, d), genre=sys.argv[4], type=sys.argv[5])
    dominator = nad.search(*sys.argv)
    with open('tmp/tmp.json', 'a') as fo:
        json.dump(dominator, fo, ensure_ascii=False)