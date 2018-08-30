# -*- coding: utf-8 -*-
# import sys
# print sys.getdefaultencoding()
import time, datetime,os
import math
import hashlib
def nn():
    pp = 1+1
millis = int(round(time.time() * 1000))
print millis

a = 1530091434483

post_time = time.localtime(int(a) / 1000)

date = datetime.datetime(post_time.tm_year, post_time.tm_mon, post_time.tm_mday, post_time.tm_hour,
                                 post_time.tm_min, post_time.tm_sec)
print date
millis = int(round(time.time() * 1000))
print millis

t = datetime.datetime.today()
print t.weekday()
if t.weekday() == 3:
    print t.weekday()

print datetime.datetime.now()


t1 = datetime.datetime.strptime("2018-08-07T10:00:00.004Z"[:-5], "%Y-%m-%dT%H:%M:%S")
print t1
# print str(t1)
dt = datetime.datetime.now()
prev_1week_first = dt - datetime.timedelta(dt.weekday()) + datetime.timedelta(weeks=-1)
prev_1week_end = prev_1week_first + datetime.timedelta(days=5)
print prev_1week_first
print prev_1week_end

print t1
print t
print date
sourceId=str(8888)
data = '{"code":"%s","part":{"brief":"{brief}"}}' % sourceId
print range(0,0)

dt = datetime.datetime.now()
datestr = datetime.datetime.strptime('2017.1.24', '%Y.%m.%d')
print dt
print datestr


dd = 1
if dd:
    print "aaa"

else:
    print "bb"

def getASCP():
    t = int(math.floor(time.time()))
    e = hex(t).upper()[2:]
    m = hashlib.md5()
    m.update(str(t).encode(encoding='utf-8'))
    i = m.hexdigest().upper()

    if len(e) != 8:
        AS = '479BB4B7254C150'
        CP = '7E0AC8874BB0985'
        return AS,CP
    n = i[0:5]
    a = i[-5:]
    s = ''
    r = ''
    for o in range(5):
        s += n[o] + e[o]
        r += e[o + 3] + a[o]

    AS = 'A1' + s + e[-3:]
    CP = e[0:3] + r + 'E1'
    return AS,CP


millis = int(round(time.time() * 1000))
print millis
print getASCP()

# ss ='{title: \'能3D打印婚纱的极致盛放获首轮数百万投资\'}'
# contentnew = eval(ss.strip())
# print contentnew
s = "中文"

if isinstance(s, unicode):
# s=u"中文"
    print "here"
    print s.encode('gb2312')
else:
# s="中文"
#     print s.encode('gb2312')
    print s.decode('utf-8')
    print s.decode('utf-8').encode('gb2312')

print ['中文']

print type('\xe4\xb8\xad\xe6\x96\x87')
print '\xe4\xb8\xad\xe6\x96\x87'
print  '\xe4\xb8\xad\xe6\x96\x87'.decode('utf-8')

ad = {"aa":1}

update_time = datetime.datetime.strptime(str(t.year)+"年"+"09月22日", "%Y年%m月%d日")
if update_time > datetime.datetime.now():
    update_time = update_time - datetime.timedelta(days=365),

print update_time


dt = datetime.datetime.now()
print dt
print dt.weekday()
print dt
i
if dt.hour == 13:
    print "hhre"

def delete():
    file_path = "download.pdf"
    if os.path.isfile(file_path):
        command = ("rm download.pdf; ")
        os.system(command)
    else:
        print 'no file'


delete()