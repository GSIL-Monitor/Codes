# -*- coding: utf-8 -*-
import sys
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()

reload(sys)
sys.setdefaultencoding("utf-8")

from itjuzi import itjuzi_next
from kr36 import kr36_next
#from demo8 import demo8_next
from mindstore import mindst_next

if __name__ == "__main__":
    ready = Event()
    gevent.spawn(itjuzi_next.start_run)
    gevent.spawn(kr36_next.start_run)
    #gevent.spawn(demo8_next.start_run) # 不再更新!
    gevent.spawn(mindst_next.start_run)
    ready.wait()