# -*- coding: utf-8 -*-
import os, sys
import subprocess
from PIL import Image
import imagehash

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper, download


#logger
loghelper.init_logger("captcha", stream=True)
logger = loghelper.get_logger("captcha")

def download():
    crawler = download.DownloadCrawler()

    url = "http://www.sgs.gov.cn/notice/captcha"
    i = 100
    while i<1000:
        i += 1
        image = crawler.get_image(url, max_retry=2)
        if image is not None:
            f = open("logs/%s.jpg" % i,'wb')
            f.write(image)
            f.close()

def convert_2_jpg():
    i = 0
    while i<1000:
        i += 1
        cmd = "convert logs/%s.jpg -threshold 80%% pics/%s.bmp" % (i,i)
        logger.info(cmd)
        p=subprocess.Popen(cmd,shell=True)
        p.wait()


def get_hash(image_path):
    """get image hash string"""
    im = Image.open(image_path)
    #antialias 抗锯齿
    #convert 转换 L 代表灰度
    im = im.resize((60, 20), Image.ANTIALIAS).convert('L')
    #avg:像素的平均值
    avg=sum(list(im.getdata()))/1200.0

    #avg和每个像素比较，得到长度64的字符串
    str=''.join(map(lambda i: '0' if i<avg else '1', im.getdata()))
    #str切割，每4个字符一组，转成16进制字符
    return ''.join(map(lambda x:'%x' % int(str[x:x+4],2), range(0,1200,4)))


def h_dis(str1,str2):
    dis = 0
    for i in range(0,len(str1)):
        if str1[i] != str2[i]:
            dis += 1
    return dis

def bmp_2_text():
    MAX = 1000
    hs = {}
    i = 0
    while i<MAX:
        i += 1
        img_path = "pics/%s.bmp" % (i)
        print img_path
        if not os.path.exists(img_path):
            continue
        #h = imagehash.average_hash(Image.open(img_path))
        h = get_hash(img_path)
        print h
        #exit()
        hs[str(i)] = h

    for i in range(1,MAX):
        if hs.has_key(str(i)):
            for j in range(i+1,MAX+1):
                if i != j and hs.has_key(str(j)):
                    dis = h_dis(hs[str(i)],hs[str(j)])
                    if dis < 160:
                        print "%s - %s : %s" % (i,j,dis)



if __name__ == "__main__":
    #convert_2_jpg()
    bmp_2_text()
    #print h_dis("1111111111111111", "1111111111001111")