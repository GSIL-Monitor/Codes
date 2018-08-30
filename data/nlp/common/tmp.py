# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
reload(sys)
sys.setdefaultencoding('utf-8')

import codecs


def aggregate():

    old = {line.split('#')[0]: line.split('#')[1].strip().split(',')
           for line in codecs.open('dict/vip.cluster.frozen', encoding='utf-8')}
    new, vip = {}, None
    for line in codecs.open('dict/vip.l12.structure', encoding='utf-8'):
        if not line.strip():
            continue
        if line.startswith('#'):
            vip = line.strip()[1:]
        else:
            new.setdefault(vip, []).extend(line.strip().split(','))
    with codecs.open('dict/vip.cluster.frozen', 'w', 'utf-8') as fo:
        for k, v in new.items():
            if k in old:
                v.extend(old.get(k))
            print k, v
            fo.write('%s#%s\n' % (k, ','.join(set([item.strip() for item in v if item.strip()]))))

if __name__ == '__main__':

    print __file__
    aggregate()
