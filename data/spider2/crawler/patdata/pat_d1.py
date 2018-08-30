# coding=utf-8
__author__ = 'Roman Podlinov'


import threading
import logging
import ftplib
import socket
import time
import sys,os
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper


#logger
loghelper.init_logger("ftp_2", stream=True)
logger = loghelper.get_logger("ftp_2")


def setInterval(interval, times = -1):
    # This will be the actual decorator,
    # with fixed interval and times parameter
    def outer_wrap(function):
        # This will be the function to be
        # called
        def wrap(*args, **kwargs):
            stop = threading.Event()

            # This is another function to be executed
            # in a different thread to simulate setInterval
            def inner_wrap():
                i = 0
                while i != times and not stop.isSet():
                    stop.wait(interval)
                    function(*args, **kwargs)
                    i += 1

            t = threading.Timer(0, inner_wrap)
            t.daemon = True
            t.start()
            return stop
        return wrap
    return outer_wrap


class PyFTPclient:
    def __init__(self, host, port, login, passwd, monitor_interval = 10):
        self.host = host
        self.port = port
        self.login = login
        self.passwd = passwd
        self.monitor_interval = monitor_interval
        self.ptr = None
        self.max_attempts = 20
        self.waiting = True


    def DownloadFile(self, dst_filename, local_filename = None):
        res = ''
        if local_filename is None:
            local_filename = dst_filename

        with open(local_filename, 'w+b') as f:
            self.ptr = f.tell()
            ftp = ftplib.FTP(timeout=60)
            ftp.set_debuglevel(2)
            ftp.set_pasv(True)

            @setInterval(self.monitor_interval)
            def monitor():
                if not self.waiting:
                    i = f.tell()
                    if self.ptr < i:
                        logger.info("%d  -  %0.1f Kb/s ---%s" % (i, (i-self.ptr)/(1024*self.monitor_interval), local_filename))
                        self.ptr = i
                    else:
                        logger.info("Something wrong")
                        # sys.exit()
                        # ftp.close()


            def connect():
                ftp.connect(self.host, self.port)
                ftp.login(self.login, self.passwd)
                # optimize socket params for download task
                # ftp.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                # ftp.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 75)
                # ftp.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)


            connect()
            ftp.voidcmd('TYPE I')
            dst_filesize = ftp.size(dst_filename)

            mon = monitor()
            while dst_filesize > f.tell():
                try:
                    connect()
                    if dst_filesize > 20000000:
                        self.waiting = False
                    # retrieve file from position where we were disconnected
                    res = ftp.retrbinary('RETR %s' % dst_filename, f.write) if f.tell() == 0 else \
                              ftp.retrbinary('RETR %s' % dst_filename, f.write, rest=f.tell())
                    logger.info("Res comes here")

                except:
                    logger.info("it is here")
                    self.max_attempts -= 1
                    if self.max_attempts == 0:
                        mon.set()
                        logger.info("out")
                        break
                    self.waiting = True
                    logger.info('waiting 10 sec...')
                    time.sleep(10)
                    logger.info('reconnect')


            mon.set() #stop monitor
            ftp.close()

            if not res.startswith('226 Transfer complete'):
                logger.info('Downloaded file {0} is not full.'.format(dst_filename))
                # os.remove(local_filename)
                return None



            return 1


if __name__ == "__main__":
    hostaddr = 'patdata1ftp.sipo.gov.cn'  # ftp地址
    username = 'cbs_xiniudata'  # 用户名
    password = '13LhYB'  # 密码
    port = 21
    file = 'CN-TXTS-10-A_中国发明专利申请公布标准化全文文本数据/20160817/20160817-1-001.ZIP'
    file2 = file.decode('utf-8').encode("GB2312")
    #        logging.basicConfig(filename='/var/log/dreamly.log',format='%(asctime)s %(levelname)s: %(message)s',level=logging.DEBUG)
    obj = PyFTPclient(hostaddr, port, username, password)
    obj.DownloadFile(file2,'20160817-1-001.ZIP')