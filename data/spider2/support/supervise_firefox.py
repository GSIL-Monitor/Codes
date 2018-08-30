import re

import time

import clean_tmp
import sys, os


reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import traceback_decorator


@traceback_decorator.try_except
def supervise_firefox():
    basepath = '/tmp'
    ls = os.listdir(basepath)
    print(ls)
    clean_pattern = 'rust_mozprofile\.\w{12}'
    rust_mozprofiles = []
    for l in ls:
        if re.search(clean_pattern, l):
            rust_mozprofiles.append(l)
    if len(rust_mozprofiles) >= 50:
        clean_tmp.rm_tmp_firefox(flag='all')
        p1 = os.popen('supervisorctl stop crawler_company_crunchbase_company')
        p2 = os.popen('supervisorctl stop beian_expand')
        print(p1.read())
        print(p2.read())
        p1.close()
        p2.close()
        raise ValueError('Firefox has something wrong!!!')
    else:
        time.sleep(60*5)