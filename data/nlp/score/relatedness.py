# coding=utf-8
__author__ = 'victor'

import os
import sys
reload(sys)
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.setdefaultencoding('utf-8')

import db as dbcon
from common import dbutil
from common.zhtools.segment import Segmenter
from common.zhtools.postagger import Tagger
from relate import NewsFeatures

import logging
from sklearn.externals import joblib


logging.getLogger('score_relate').handlers = []
logger_relate = logging.getLogger('score_relate')
logger_relate.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_relate.addHandler(stream_handler)


class RelatednessScorer(object):

    global logger_relate

    def __init__(self, model='default'):

        # self.segmenter = Segmenter()
        self.tagger = Tagger(cname=True)
        # self.extractor = Extractor(record=False)
        if model == 'easy':
            self.clf = joblib.load(os.path.join(os.path.split(os.path.realpath(__file__))[0],
                                                'dumps/backup/news.score.lrmodel'))
            self.vec = joblib.load(os.path.join(os.path.split(os.path.realpath(__file__))[0],
                                                'dumps/backup/news.featurizer'))
        else:
            self.clf = joblib.load(os.path.join(os.path.split(os.path.realpath(__file__))[0],
                                                'dumps/news.score.lrmodel'))
            self.vec = joblib.load(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dumps/news.featurizer'))
        self.nf = NewsFeatures()
        self.db = dbcon.connect_torndb()

    def compare(self, cid, **kwargs):

        logger_relate.info('Compare news of company#%s' % cid)
        instance = dict(**kwargs)
        if instance.get('name'):
            self.tagger.add_word(instance.get('name'), tag='cn')
        name, title, content = instance.get('name'), instance.get('title'), instance.get('content')

        if len(content) <= 20:
            return False, 0
        # print self.nf.featurize(cid, name=name, title=title, content=content)
        news = self.vec.transform([self.nf.featurize(cid, name=name, title=title, content=content)])
        result = self.clf.predict_proba(news)[0]
        return (float(result[1]) > float(result[0])), round(result[1], 4)


        # score_ner = self.__compare_postag(name, title, content)
        # # if score_ner > 0.39:
        # #     return True
        # score_tag = self.__compare_tag(cid, content)
        # if score_tag > 0.19 or (score_ner+score_tag) > 0.49:
        #     return True
        # return False

    # def __compare_postag(self, name, title, content):
    #
    #     score = 0
    #     if title and title.strip():
    #         title = self.tagger.tag(title)
    #         matches = [x[0] for x in title if x[1] == 'cn']
    #         score += 0.75 * (matches.count(name) > 0)
    #     if content and content.strip():
    #         content = list(self.tagger.tag(content))
    #         matches = [x[0] for x in content if x[1] == 'cn']
    #         score += 0.5 * (matches.count(name)/(len(matches) or 1))
    #     return score
    #
    # def __compare_tag(self, cid, c2):
    #
    #     # c1 = dbutil.get_company_solid_description(self.db, cid)
    #     # if (not c1.strip()) or (not c2.strip()):
    #     #     return -1
    #     # words1, words2 = list(self.segmenter.cut(c1)), list(self.segmenter.cut(c2))
    #     # tags1, tags2 = self.extractor.extract(words1), self.extractor.extract(words2)
    #
    #     if not c2.strip():
    #         return -1
    #     tags1 = [(t[1], t[2]) for t in dbutil.get_company_tags_idname(self.db, cid)]
    #     words2 = list(self.segmenter.cut(c2))
    #     tags2 = self.extractor.extract(self.extractor.extract(words2))
    #     if not (tags1 and tags2):
    #         return -1
    #     if (isinstance(tags1, list) and len(tags1) == 0) or (isinstance(tags2, list) and len(tags2) == 0):
    #         return -1
    #
    #     # compute the weigted Jaccard Similarity of two tag set
    #     sum_up, sum_down = 0, 0
    #     tags1, tags2 = dict(tags1), dict(tags2)
    #     for tag in (set(tags1.keys()) | set(tags2.keys())):
    #         sum_up += min(tags1.get(tag, 0), tags2.get(tag, 0))
    #         sum_down += max(tags1.get(tag, 0), tags2.get(tag, 0))
    #     return float(sum_up)/sum_down

if __name__ == '__main__':

    print __file__
    s = RelatednessScorer()
    title = u'真格投他600万  4个黑客干了个网络安全公司 3个月已服务30家客户'
    content = u'长亭科技核心成员，从左至右分别是联合创始人陈宇森、创始人朱文雷、联合创始人杨坤。 文| 铅笔道 记者 薛婷 ► 导读： 上海浦东证大喜马拉雅中心内，三层观礼台挤满了800多位智能硬件爱好者。观众席灯光暗下来，现场安静，所有人将目光汇集到舞台中央。 3个小伙子正在表演破解7款不同的摄像头。 在他们的操作下，不仅攻破了摄像头，获取到拍摄画面，还能控制摄像头的转向，比如7款摄像头同时向左转、向右转。 ◆ GeekPwn比赛现场 “非常漂亮”一旁的评委TombKeeper（于旸，人称“黑客教主”）在鼓掌。 3个小伙子来自一家公司——长亭科技。 长亭科技的创始人在3年前就相互认识，他们同在黑客战队蓝莲花打攻防比赛，2013年成为华人世界历史上首支成功闯入世界黑客大会DEFCON CTF全球总决赛的战队。去年7月，几个成员面临毕业，放弃了大公司的Offer，自己成立了长亭科技。 一年时间，他们尝试了不同方向的业务。 今年7月，他们把主营业务定位为（中小型）企业提供网络安全服务，以安全检测、提供防护产品为主： 企业提交申请、签订测试授权协议，长亭对企业线上系统进行免费安全测试。若发现安全隐患，便会评估风险，并提供防护产品，若决定购买，服务报价会根据隐患的危害等级确定。 9月，他们对客户推出“0元起步的企业安全服务” 。至今，长亭科技已服务30家企业，以P2P公司、电商为主，客单价在15-20万之间，且已有三家公司意向签定年度合作协议。 三个月前，该项目已获得真格基金600万元人民币天使融资。 一年尝试方向 “毕业后有什么打算？” “先找个公司干两年。” “不如我们一起搞个公司自己干。” 去年5月，陈宇森和朱文雷等人在筹备“百度杯全国攻防大赛”。 二人同住一个房间，朱文雷提出创业打算。 彼时，陈宇森即将在浙大毕业，手里已握着阿里、360等几个公司的Offer。 “我自己也喜欢折腾，创业应该会比去大公司更加符合自己的性格。”陈没有犹豫，爽快地答应朱文雷的提议。 去年7月，包括朱文雷、陈宇森在内的4个人成立了“长亭科技”。 创始团队均是来自黑客战队Blue-Lotus（蓝莲花）的主要成员，包括队长。其他成员主要来自清华、浙大、牛津等学校。 过去两年，他们拿下了国内大大小小的安全攻防大赛冠军 ，如360、阿里巴巴、西安电子科技大学、杭州电子科技大学、中国国家测评中心等单位举办的比赛。 2013年，他们又作为主力成为华人世界历史上首支成功闯入世界黑客大会DEFCONCTF全球总决赛的战队成员。 “去年和今年，我们都打进了决赛，成绩都是全球第五。”陈宇森说。 初期凭借几年的技术积累，4人尝试了多个方向。 做过移动安全、工控设备、网站安全、攻防平台等方面的一些项目。“甚至还做过外包开发类项目，帮别人写一个数据收集系统。“陈笑称，4个人更像一个工作室，在清华的启迪之星摸索方向。 尝试了近一年，4人决定该把方向聚焦，将业务更贴近商业化运作。 他们把做过的项目结合市场情况逐一分析。最终，他们将方向定为针对中小型企业的网络安全服务，业务以安全检测、提供防护产品为主。 一方面，大家对安全的重视程度提高。 “国 内的互联网企业有两种状态，一种是知道自己被黑客攻击了，一种是不知道但也被黑客攻击过。在网络安全没有保障的情况下，互联网企业很容易被攻击甚至因为攻 击倒闭。一些电商、P2B金融金融公司离钱很近，安全做不好，平台损失很大。”陈说，初创公司会更注重安全检测的效果，而不是考虑你是大团队、小团队，这 将利于他们切入市场。 另一方面，安全服务成本不低 。 “算下来差不多要8000元/人/天。”陈说，他们想提供实实在在的服务，让客户觉得服务值那个价。同时，利用技术手段将安全检测的流程自动化来压缩成本。 0 元起步 今年6月，长亭团队自主研发出了SQL注入攻击检测与防御引擎SQLChop ，并入选世界最高级别黑客大会BlackHat。8月，4人将这个来自中国的防御型产品带上了世界黑客大会的舞台。 同期，4人将产品推向市场。 6月中，他们遇到了一个特别的客户：以太资本。 当时，长亭的客单价在20万左右，说服以太接受并不容易。 “正好他们CTO是朱文雷的清华学弟，他提议我们可以先不收钱，但会签个授权协议让我们做，看最后的效果收费。这样比较容易让周子敬（以太资本创始人）看到他们的价值。”陈说，服务结束后，以太很满意，也很痛快给了钱。 由此，他们将此收费模式标准化，推出了“0元起步的企业安全服务”计划。 “我们先跟客户签一个免费授权协议，为他的平台进行一次轻量级的体检，将发现的问题和可能带来的危害告诉客户，接下来由客户选择，要不要用收费的全面体检和修复建议。” 陈补充，若检查出安全问题，他们会在企业授权的前提下，在真实环境中对系统漏洞进行攻击 ，这样安全隐患就会以比较直观的方式展现在企业面前。且攻击会点到为止，不会让企业受到损失。 所有的服务都是按最终的效果付费。 相比之下，市面上很常见的方式是众测，企业对接的是游荡的个人黑客，按发现的漏洞个数收费。“我觉得企业没必要知道他有多少漏洞，他更需要了解漏洞造成的结果。” 他解释，长亭会按漏洞所造成的危害等级区别定价。 “比如我为你发现的一系列漏洞造成的危害很低，收费就会非常低。假如我为你发现一些漏洞，能造成你服务器被人控制，整个数据库能被人偷走甚至更严重的后果，这样收费会高一些。” 模式初见成效。 7月，他们已服务了2、3家大单客户。同期，4人启动了天使轮融资。一年来，他们没扩张，保持盈亏平衡。“我们对融资的态度很谨慎。”陈说。 7月底，长亭科技获得真格基金的600万天使投资。 “在咖啡馆和李建威（真格基金合伙人）聊了2小时，他认为我们有技术基础，觉得这事能成，就投了。”陈宇森笑着回忆，“当时TS都没签，直接签了最终的打款协议。” 已服务30家企业 融资后，4人的当务之急是将服务标准化，主要体现在检测报告、解决方案等。 “之前我们只关心技术，检测报告一般只有10几页。”陈说，原来觉得厚厚一沓的报告有些浪费时间。 后来，4人沉下心去学，发现很多解释是有必要的，要让技术差的人也能看懂。 他打趣道：“我们现在每份报告有40多页，客户看了也开心。” 之后，他们陆续接了不少客户订。 过程中，陈宇森发现一些非交易平台并不愿意付费。“比如曾做过一些2C产品的安全监测，发现结果很危险。但他就是不愿意付钱，觉得用户隐私不重要。” 陈放弃了这类用户，将客户聚焦在P2P公司和电商 ，如人人贷、21cake、理财范、E租宝、有利等。“蓝色光标、同程旅游、途牛等也在找我们。”陈说。 目前，长亭有12个员工，都是技术，没有商务人员，陈宇森自己也会出去跑业务。 “有一次，想去中关村的互联网金融大厦做BD，里面都是金融公司。结果在下面转了两圈，才敢上电梯，去了12层，走到一家公司门口，不敢进去。又下来转了两圈，才上去敲了那家公司的门。”陈自嘲道，克服了一道心理障碍。 7月以来，长亭科技已服务了30家企业，多以P2P公司、电商为主。 客单价在15-20万之间。所有服务的企业中，付款率为80%。“已有三家公司想跟我们签年度合作协议，如E租宝、快用手机助手、有利。” 陈说，未来并不急于增加用户数量，而会重点扩展可以长期合作的企业用户。 近期，他们主要任务是打磨自己的防护设备。 “给企业发现问题，他去修改代码很累。我们若能有一些比较好的防护设备给客户使用，他会更能接受，可以形成服务的闭环。”其防护设备技术已完善，处于用户测试阶段。 此外，他们将继续加快服务流程自动化。 “现在测试很快，写报告很麻烦，如果把这一步自动化，将节省很多人力成本。”长亭团队理想的标准是，整套服务流程达到80%自动化，但目前只做到10%多。 ◆ 去年，长亭小伙伴团建，这是他们滑雪后留下的合影。 在做产品和扩展用户的同时，他们还坚持做一些安全领域前沿问题研究。10月24日，在上海GeekPwn安全极客嘉年华上，长亭团队分别演示了破解7款知名品牌摄像头、破解Pos机、破解路由器。最终，他们成功获得了一类奖金中的第三名，共计32万奖金。 来！已融资的项目求报道，请加微信号shoujiyezi5415； 文章原创，如需转载，请加微信号meera003；'
    print s.compare(18640, name=u'长亭科技', title=title, content=content)
    # title = u'《新白娘子传奇》续集，怎么这个套路！？'
    # content = u'《新白娘子传奇》续集，怎么这个套路！？'
    # print s.compare(141106, name=u'传奇', title=title, content=content)