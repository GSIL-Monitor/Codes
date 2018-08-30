# coding=utf-8
__author__ = 'victor'

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('..')

import re
import datetime
import logging
import torndb
import pandas as pd
from copy import copy
from recruit import nlpconfig, dbutil
from classifier import PositionClassifier


num = re.compile('(\d+)')

logging.getLogger('summarize').handlers = []
logger_summary = logging.getLogger('summarize')
logger_summary.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_summary.addHandler(stream_handler)


fresh_salary = {
    1: 5.4,
    2: 5,
    3: 5.7,
    4: 5,
    5: 5,
    6: 3.7
}

speed_db_mapping = {
    0: 2301,
    1: 2302,
    2: 2303,
    3: 2304
}

salary_db_mapping = {
    0: 2401,
    1: 2402,
    2: 2403,
    3: 2404
}


class Recruit(object):

    def __init__(self):

        self.position_clf = PositionClassifier()
        self.speed = {}
        self.today = datetime.datetime.today().date()
        self.df = None
        self.__train()

    def __train(self):

        self.df = self.__load_all()
        logger_summary.info('data loaded')

        # close period
        for position in self.position_clf.get_first_positions():
            data = self.df[self.df['first_category'] == position]
            num_positions = data.size
            data = data[(self.today-data['modify_date']).map(lambda x: x.astype('timedelta64[D]').astype(int)) > 2]
            data = (data.modify_date - data.create_date).map(lambda x: x.astype('timedelta64[D]').astype(int))
            self.speed[position] = {
                'total': num_positions,
                'closed': data.size,
                'mean': data.mean(),
                'median': data.median(),
                'std': data.std()}

        logger_summary.info('model trained')

    def evaluate(self, cid, timeperiod=None):

        global salary_db_mapping, speed_db_mapping
        # prepare data to compare
        eva = self.df[self.df['cid'] == cid]
        print eva.sort(columns='create_date')
        if eva.size == 0:
            return
        db = torndb.Connection(**nlpconfig.get_mysql_config_tshbao())
        similars = dbutil.get_similar_companies(db, cid)
        db.close()
        if not similars:
            return
        similars = self.df[self.df['cid'].isin(similars)]
        if timeperiod:
            try:
                start, end = timeperiod
            except Exception, e:
                logger_summary.warning('%s#time period bad format' % cid)

        # compare first category with the most position counts, aka focus
        focus = eva.first_category.value_counts().idxmax()
        eva_focus = eva[eva['first_category'] == focus]
        similars_focus = similars[similars['first_category'] == focus]
        salary_cmp_similars = self.__cmp_salary_similars(eva_focus, similars_focus)
        speed_cmp_general = self.__cmp_speed_general(eva_focus, self.speed.get(focus))
        return focus, {
            'isMajor': 'Y',
            'similarSalary': salary_db_mapping.get(salary_cmp_similars),
            'overallSpeed': speed_db_mapping.get(speed_cmp_general)
        }

    def evaluate_all(self):

        db = torndb.Connection(**nlpconfig.get_mysql_config_tshbao())
        for cid in dbutil.get_job_companies(db):
            try:
                field, result = self.evaluate(cid)
                dbutil.update_recruit_summary(db, cid, field, result)
                logger_summary.info('%s recruit info summarized' % cid)
            except Exception, e:
                logger_summary.exception('%s#%s' % (cid, e))
        db.close()

    def __cmp_speed_general(self, a, ave):

        a = a[((self.today-a['modify_date']).map(lambda x: x.astype('timedelta64[D]').astype(int)) > 2) |
              ((a['modify_date'] - a['create_date']).map(lambda x: x.astype('timedelta64[D]').astype(int))
               > ave.get('mean'))]
        a = (a.modify_date - a.create_date).map(lambda x: x.astype('timedelta64[D]').astype(int))
        comp = 0
        division = float(a.mean()-ave.get('mean'))/ave.get('mean')
        if division > 0.35:
            comp += 0  # 2301, 较慢
        elif 0 < division <= 0.35:
            comp += 1  # 2302, 一般
        elif -0.35 < division <= 0:
            comp += 2  # 2303，较快
        else:
            comp += 3  # 2304，很快
        return comp

    def __cmp_salary_similars(self, a, b):

        salary_a = tuple([a.salary_a.mean(), a.salary_a.median()])
        salary_b = tuple([b.salary_a.mean(), b.salary_a.median()])
        comp = 0
        for index, aspect_a in enumerate(salary_a):
            division = (salary_b[index]-aspect_a)/aspect_a
            if division > 0.35:
                comp += 0  # 2401, 较高
            elif 0 < division <= 0.35:
                comp += 1  # 2402，不错
            elif -0.35 < division <= 0:
                comp += 2  # 2403，一般
            else:
                comp += 3  # 2404，较低
        return int(round(float(comp)/len(salary_a)))

    def __load_all(self):

        return self.__load(None)

    def __load(self, cids):

        names = ['cid', 'position', 'education', 'experience_l', 'experience_u', 'salary_l', 'salary_u', 'salary_a',
                 'headcount', 'city', 'create_date', 'modify_date', 'first_category']
        df = []
        db = torndb.Connection(**nlpconfig.get_mysql_config_tshbao())
        work_year_mapping = dbutil.get_job_work_year(db)
        results = dbutil.get_lagou_jobs(db, cids)
        if not results:
            return
        for result in results:
            cid = result.companyId
            try:
                # job = json.loads(job.decode('unicode_escape').replace('\\', '/'))
                item = {}
                item['cid'] = cid
                # item['pid'] = job.get('positionId')
                item['first_category'] = copy(self.position_clf.classify_first(result.get('positionName')))
                item['position'] = result.get('positionName')
                # item['education'] = job.get('education')
                item['experience_l'], item['experience_u'] = work_year_mapping.get(result.get('workYear', ''))
                item['salary_l'], item['salary_u'] = self.__get_salary(result.get('salary', ''))
                item['salary_a'] = self.__average_salary(item['first_category'], item['salary_l'], item['salary_u'],
                                                         item['experience_l'], item['experience_u'])
                # item['headcount'] = hc
                # item['city'] = job.get('city')
                item['create_date'] = result.get('bornTime').date()
                item['modify_date'] = result.get('updateTime').date()
                df.append(item)
                # logger_summary.info('%s#data loaded' % cid)
            except Exception, e:
                logger_summary.error('%s#error %s' % (cid, e))
        df = pd.DataFrame(df)
        db.close()
        return df

    def __get_modify_time(self, t):

        try:
            return datetime.datetime.strptime(t, '%Y-%m-%d').date()
        except Exception, e:
            return datetime.datetime.today().date()

    def __get_experience(self, e):

        global num
        if u'-' in e:
            return map(lambda x: int(x), num.findall(e))[0:2]
        else:
            return 0, 0.5

    def __get_salary(self, s):

        global num
        if u'-' in s:
            return map(lambda x: int(x), num.findall(s))[0:2]
        else:
            nums = num.findall(s)
            return int(nums[0]), int(nums[0])+0.5

    def __average_salary(self, first_cate, s1, s2, e1, e2):

        """
        calculate salary with binominal regression f(x)=ax^2+bx+c, with (e1, s1), (e2, s2) and (0, c)
        :return: salary of the 1-year experienced
        """
        global fresh_salary
        if e1 == 0:
            return s2
        c = fresh_salary.get(first_cate)
        a = float((s1-c)*e2-(s2-c)*e1)/((e1-e2)*e1*e2)
        b = (s1-c-(e1**2)*a)/e1
        return round(a+b+c, 4)


def evaluate_all():

    r = Recruit()
    r.evaluate_all()


if __name__ == '__main__':

    print __file__

    if sys.argv[1] == 'all' or sys.argv[1] == 'period':
        evaluate_all()
    else:
        r = Recruit()
        cid = 20292
        db = torndb.Connection(**nlpconfig.get_mysql_config_tshbao())
        field, result = r.evaluate(cid)
        print field, result
        dbutil.update_recruit_summary(db, cid, field, result)
        db.close()