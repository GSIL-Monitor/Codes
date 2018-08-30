# -*- coding: utf-8 -*-
import os, sys,random
import urllib2
import urllib
import json
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import GlobalValues

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,util

#logger
loghelper.init_logger("crawler_lagou_company", stream=True)
logger = loghelper.get_logger("crawler_lagou_company")

KEYS=[128222,127835,127797,127756,127735,127666,127662,127661,127659,127657,127655,127654,127653,127652,127650,127647,127646,127645,127643,127641,127640,127639,127637,127633,127630,127628,127595,127590,127513,127495,127446,127291,127207,127147,126764,126733,126381,126354,126276,126185,125909,125666,125462,125346,125323,125190,125142,125139,124756,124564,124272,124163,123902,91455,123773,123735,123427,123422,123374,123321,123112,123082,123059,123057,123005,122906,97293,88986,82664,79139,76922,75699,74550,73824,68782,67825,64826,60486,57131,54276,52143,51787,51736,48878,46120,44786,40176,35981,24828,17783,14481,9989,122453,122452,122383,122380,122234,122215,122139,122123,121992,121991,121951,121894,121825,121464,121463,121433,121370,121222,121218,121068,121060,121028,120804,120743,120739,120497,120483,120423,120409,120295,120230,120163,120042,119982,119862,119852,119784,119624,119541,119417,119360,119193,119184,119169,118936,118858,118729,118643,118625,118617,118584,118425,118132,118094,118026,117473,117464,117425,117406,117317,117156,117134,117084,117024,116942,116858,116603,116411,116236,116103,115814,115535,115338,115255,115056,114945,114873,114551,114202,114019,113463,113413,99658,99351,99043,99042,98888,98887,98819,98783,98563,98546,98249,98117,98017,97457,96764,96692,96551,96036,95826,95541,95284,95121,94659,93367,93053,92572,92001,91430,90916,90322,89654,89443,88466,87639,87169,87159,86919,86644,86391,85981,85385,91,250,740,1774,2024,2176,2202,4184,4780,4798,5026,5504,5978,6296,9283,10191,10329,11055,11237,11873,11941,12455,13513,13773,13981,14221,15959,16883,17459,18177,20525,21742,23726,24751,25381,26638,26953,27875,28675,28769,29137,29759,31101,31105,32811,36026,36119,36699,36825,37884,40019,40213,42644,43479,43918,44208,44544,46216,46602,47131,47134,47406,47771,48687,48880,49034,49094,49131,51325,52890,54228,54302,55766,55833,55867,56294,57627,57738,57773,58267,58460,59561,60036,61469,62511,63064,63302,63698,63870,64571,65145,65150,65538,66052,66981,67314,68033,69214,69466,69899,70753,71569,71656,71708,72138,73315,73318,73329,73968,74332,74504,74721,75572,76039,76299,76529,76667,77028,77954,78478,78748,78778,79646,79941,80404,81487,81591,82550,82616,82950,83535,83967,84045,84194,84262,84263,84604,84761,113296,113265,113232,113099,113037,112974,112901,112746,112720,112646,112643,112497,111986,111721,111714,111665,111617,111261,111200,111127,111101,111070,111064,110701,110694,110341,110181,110127,109555,109436,109344,109307,109261,109108,109030,109028,108985,108749,108586,108500,108434,108306,107985,107872,107325,107287,105356,102012,101112,101773,102060,104484,104604,105198,106959,106956,10711,107030,10737,107126,10891,11261,12255,12095,12625,12787,12889,13277,13301,13689,14147,14163,14441,14903,15093,1588,16531,16615,16367,16849,17497,17481,17469,17637,17881,18213,18265,18781,1930,19175,19631,19571,19439,19773,19755,20357,20677,20409,20423,2120,21209,21501,21810,22312,22345,22608,22574,22612,22639,22721,23348,23466,23414,23554,23512,23605,23737,23620,24029,23922,24402,24605,24458,24641,24629,24702,24876,24891,24820,24835,25020,25002,25306,25328,25399,25546,25684,25858,26031,26003,26137,26249,26203,26208,26289,2662,26818,26714,2692,27259,27383,27909,27880,28194,28078,28166,28227,28571,28577,28549,28499,28885,29024,29095,29237,29270,29261,2932,29753,29770,29679,3000,299,30092,30186,30275,30308,30555,30861,30840,3082,31065,31434,31540,31808,32089,32384,32285,32424,32453,32745,32656,32617,32678,3278,32946,33170,3332,33669,33676,33998,34221,34428,34686,34902,34906,3534,35836,35744,35961,35948,35890,36257,36318,36464,36645,36654,36963,36821,37034,37311,37980,38098,38198,38164,38341,38279,38404,38453,38976,38916,39052,38990,39183,39173,39420,39600,39716,39652,39896,39831,39912,40022,39972,40334,40304,40330,40729,40989,40947,41162,41268,41376,41366,415,41917,42043,42236,42219,42407,42604,42503,42742,42919,42867,43070,43395,43505,4360,43797,43900,43923,43937,44008,43948,4418,44210,44592,44564,44677,44736,44805,44821,45311,45450,45499,45704,4598,46129,46255,463,46549,46627,46828,46807,47164,47644,47670,47657,47725,47699,47901,47890,48191,48009,48246,48376,48534,48714,48697,48702,48823,49181,49100,49166,49174,49025,49265,49536,49445,49727,50013,50262,50241,50455,50519,50565,50776,51184,51230,51253,51193,51544,51848,51772,51744,51843,51930,51913,5200,52193,52201,52384,52268,52319,52464,52715,53376,53382,53751,53757,53978,53998,53982,539,53938,54484,54775,54863,55001,55022,55213,55210,55128,55306,55769,56042,56229,56099,56092,56571,56929,56997,56905,57080,57148,57309,57238,57312,57539,57568,57656,57754,58147,58154,58645,58753,58800,58919,58988,59237,59305,59397,59441,59471,59841,59976,60206,60462,60453,60731,60961,61035,61222,61152,61603,61705,62033,62330,62433,62538,62584,62681,6290,62991,62967,63142,6326,63266,63356,63565,63605,63730,64331,64517,64552,64592,64891,65007,65071,65227,65323,65499,65458,65688,65841,66250,66347,66383,66558,66634,66710,66746,66725,66705,66712,67487,67540,67667,67840,68241,68129,6840,68318,69019,69263,69683,69663,69940,7008,70167,701,70205,70195,70209,70495,70696,70855,70812,7078,71063,71157,71204,71572,71479,71544,71525,71856,7179,72226,72259,72147,72474,72487,72777,72749,72758,72821,72956,72938,72934,73000,7338,74123,74116,74185,74236,74484,74346,74451,74718,74938,74750,75036,75437,75392,75727,75629,75617,7590,75922,76147,76075,76050,76241,76450,76517,76417,76647,76726,77113,77929,77879,78189,78080,78062,78323,78389,78992,79040,79525,79666,79908,79849,80096,80358,80572,80588,80804,81269,81218,81521,81484,8172,81897,8205,81914,82092,82248,82292,82641,83060,82925,83212,83343,83878,83953,83919,83911,84019,83955,84166,84371,84494,84842,84808,85029,85057,85164,85044,8543,85912,86060,85894,85982,86122,86466,86383,86435,86542,86514,86901,8701,8695,87010,87423,87909,87973,87835,88125,88025,88113,88367,88333,88381,88450,88546,88509,88503,88487,88605,88602,88607,88660,8859,88802,88765,89161,89465,89396,89535,89745,90046,90030,89926,90446,90568,90569,90486,90451,90930,91118,91142,91152,91138,91520,91604,91572,91538,9171,91758,91613,92102,91992,92200,92413,92681,92654,92545,92592,9285,92812,92704,92991,92982,93162,93349,93592,93749,93731,93857,93890,93967,94050,94240,94534,94667,94916,94976,95185,95463,9609,96042,95954,96252,96201,96229,96324,96455,96298,96581,96627,96669,96637,96542,96498,96722,96851,96955,96938,96930,97374,97354,97231,97317,97491,97540,97483,97467,97633,97620,98144,98132,98632,98457,98842,98777,99407,99415,99850,99962,106937,106928,106890,106812,106771,106750,106700,106532,106512,106446,106404,106401,106377,106353,106249,106230,106221,106184,106096,106088,106050,105848,105774,105722,105711,105696,105669,105587,105551,105528,105485,105436,105432,105426,105421,105377,105326,105291,105252,105219,105209,105151,105136,105066,104958,104789,104681,104644,104631,104523,104502,104353,104220,104216,104153,103939,103914,103902,103882,103845,103788,103740,103725,103705,103685,103648,103641,103576,103560,103546,103501,103482,103380,103356,103277,103266,103188,103068,102832,102735,102732,102593,102579,102576,102562,102555,102533,102507,102403,102399,102307,102173,102170,102118,102111,102105,102011,101848,101847,101832,101774,101698,101672,101664,101616,101591,101552,101437,101472,101418,101232,101207,101143,100996,100974,100966,100901,100872,100719,100626,100498,100427,100416,100396,100335,100065,100003]
SOURCE=13050
TYPE=36001

class LagouCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=15):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    # 实现
    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " "+ url)

        if title.find("访问验证") >= 0:
            #logger.info(content)
            return False
        if title.find("拉勾网") >= 0:
            return True
        #logger.info(content)
        return False

class LagouJobCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)


    def is_crawl_success(self, url, content):
        if content.find('操作成功') == -1:
            logger.info(content)
            return False
        return True

crawler_job = LagouJobCrawler()

def has_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    #logger.info("title: " + title)

    temp = title.split("-")

    if len(temp) < 3:
        return False
    if temp[0].strip() == "找工作":
        return False
    return True


def has_job_content(content):
    if content is not None:
        try:
            j = json.loads(content)
        except:
            logger.info("Not json content")
            logger.info(content)
            return False

        if j.has_key("message") and j["message"] == "操作成功":
            return True
        else:
            logger.info("wrong json content")
            logger.info(content)
            return False
    else:
        logger.info("Fail to get content")

    return False


def process(g, crawler, url, key, content):
    #logger.info(content)
    if has_content(content):
        logger.info(key)
        crawler.save(SOURCE, TYPE, url, key, content)
        #g.latestIncr()
        jobs_url = "http://www.lagou.com/gongsi/j%s.html" % key
        #job_url = "http://www.lagou.com/gongsi/searchPosition.json?companyId=%s&pageSize=1000" % key
        retry_times_job = 0
        result = crawler.crawl(jobs_url)
        while True:
            if result['get'] == 'success' and result["redirect_url"] == jobs_url:
                 break
            else:
                result = crawler.crawl(jobs_url)
                #continue
            retry_times_job += 1

            if retry_times_job > 20:
                result["content"] = "no_content"
                break

        d = pq((html.fromstring(result['content'].decode("utf-8"))))
        position_types = d('div.item_con_filter> ul> li').text().split(" ")
        logger.info(json.dumps(position_types, ensure_ascii=False, cls=util.CJsonEncoder))
        jobs = {}
        for type in position_types:
            if type == '全部' or type.strip() == "":
                continue
            job_url = "http://www.lagou.com/gongsi/searchPosition.json?companyId=%s&pageSize=1000&positionFirstType=%s" % (key, urllib.quote(type.encode('utf-8')))
            result_job = crawler_job.crawl(job_url)
            while True:
                if result_job['get'] == 'success':
                    break
                else:
                    result_job = crawler_job.crawl(job_url)
                    continue
            content_job = result_job["content"]
            if has_job_content(content_job):
                jobs[type] = json.loads(content_job)
                jobs["version"] = 2

        logger.info(json.dumps(jobs, ensure_ascii=False, cls=util.CJsonEncoder))
        logger.info(len(jobs))
        if len(jobs) > 0:
            crawler.save(SOURCE, 36010, jobs_url, key, jobs)
        '''
        if has_job_content(content_job):
            jobs = json.loads(content_job)
            #job=json.dumps(jobs, ensure_ascii=False)
            #logger.info(content_job)
            #logger.info(job)
            # time.sleep(random.randint(3,8))
            crawler.save(g.SOURCE,36010, job_url, key, jobs)
        '''

def run(g, crawler):
    while True:
        if len(KEYS) == 0:
            return
        key = KEYS.pop(0)
        url = "http://www.lagou.com/gongsi/%s.html" % key
        retry_times = 0
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                #logger.info(result["content"])
                try:
                    process(g, crawler, url, key, result['content'])
                except Exception,ex:
                    logger.exception(ex)
                break
            elif result['get'] == 'redirect':
                logger.info("Redirect: %s", result["url"])
                pass

            retry_times += 1
            if retry_times > 40:
                break
                #break



def start_run(concurrent_num, flag):
    while True:
        logger.info("Lagou company %s start...", flag)

        #g = GlobalValues.GlobalValues(13050, 36001, flag, back=8)
        g=1

        #run(g, LagouCrawler())
        threads = [gevent.spawn(run, g, LagouCrawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("Lagou company %s end.", flag)

        if flag == "incr":
            gevent.sleep(60*30)        #30 minutes
        else:
            gevent.sleep(86400*3)   #3 days

        #break

if __name__ == "__main__":

    if len(sys.argv) > 1:
        flag = sys.argv[1]
    else:
        flag = "incr"

    if flag == "incr":
        concurrent_num = 1
    else:
        concurrent_num = 23

    start_run(concurrent_num, flag)