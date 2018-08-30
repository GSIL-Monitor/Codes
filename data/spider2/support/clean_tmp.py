import os
import re
import time
import shutil

import sys


def rm_tmp_firefox(flag='incr'):
    basepath = '/tmp'
    clean_pattern = 'rust_mozprofile\.\w{12}'
    clean_pattern2 = 'tmp\w{6}'
    clean_pattern3 = 'tmpaddon-.*'
    ls = os.listdir(basepath)
    for l in ls:
        if re.search(clean_pattern,l) or re.search(clean_pattern2,l) or re.search(clean_pattern3,l):
            clean_path = basepath + '/' + l
            file_time = os.path.getctime(clean_path)
            clean_time = time.time() - file_time
            if flag == 'incr':
                hours = 60*60*5
            else:
                hours = 0
            if clean_time > hours:
                try:
                    shutil.rmtree(clean_path)
                except:
                    os.remove(clean_path)
                print('clean file | path :%s | createtime:%s done'%(clean_path, time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(file_time))))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        rm_tmp_firefox(flag='all')
    else:
        rm_tmp_firefox()