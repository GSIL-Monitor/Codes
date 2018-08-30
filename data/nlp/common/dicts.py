# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
reload(sys)
sys.setdefaultencoding('utf-8')

import codecs
import urlparse


def get_sector_extend():

    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dict/sector.cluster.frozen')
    with codecs.open(path, encoding='utf-8') as f:
        extend = {line.split('#')[0]: line.split('#')[1].split(',') for line in f}
    return extend


def get_vip_succession():

    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dict/vip.l12.structure')
    new, vip = {}, None
    for line in codecs.open(path, encoding='utf-8'):
        if not line.strip():
            continue
        if line.startswith('#'):
            vip = line.strip()[1:]
        else:
            new.setdefault(vip, []).extend(line.strip().split(','))
    return new


def get_known_angels():

    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dict/investors_famous')
    return set([int(line.strip().split('#')[0]) for line in codecs.open(path, encoding='utf-8')])


def get_known_company_source():

    return [13020, 13022, 13030,
            13100, 13101, 13102, 13103, 13104]


def get_trust_news_source():

    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dict/news.source')
    return set([urlparse.urlparse(line.strip()).netloc for line in codecs.open(path, encoding='utf-8')])


def get_important_news_source():

    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dict/news.important.source')
    return set([int(line.strip()) for line in codecs.open(path, encoding='utf-8')])


def get_news_sources4tag():

    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dict/11800')
    return {int(line.split('#')[0]): int(line.split('#')[1]) for line in open(path)}


def get_report_authors():

    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dict/11802')
    author_tag_dict = {}
    with codecs.open(path, encoding='utf-8') as f:
        for line in f:
            pairs = line.strip().split('#')
            tagid = int(pairs[0])
            for author in pairs[1:]:
                author_tag_dict[author] = tagid
    return author_tag_dict


def get_wechat4tag():

    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dict/11804')
    pairs = [line.strip().split('#') for line in open(path)]
    return {unicode(pair[0]): int(pair[1]) for pair in pairs}


def get_zhihu4tag():

    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dict/11805')
    pairs = [line.strip().split('#') for line in open(path)]
    return {unicode(pair[0]): int(pair[1]) for pair in pairs}


def get_yellow_tags_name():

    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'thesaurus/yellow.name')
    return [line.strip() for line in codecs.open(path, encoding='utf-8')]


def get_common_cname():

    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dict/common.cname')
    return set([line.strip() for line in codecs.open(path, encoding='utf-8') if line.strip()])


def get_common_cid():

    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dict/common.cid')
    return set([line.strip() for line in codecs.open(path, encoding='utf-8')])


def get_company_top500():

    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dict/company_top500')
    return set([line.strip() for line in codecs.open(path, encoding='utf-8')])


def get_recruit_managment():

    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dict/recruit.management')
    return set([line.strip() for line in codecs.open(path, encoding='utf-8')])


# kailu - 20161216
def get_gangs_relatives():

    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dict/gangs')
    return [line.strip().split("#") for line in codecs.open(path, mode="r", encoding="utf-8")]


if __name__ == '__main__':

    print get_trust_news_source()