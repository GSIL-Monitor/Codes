#coding=utf-8
'''
	ftp自动下载、自动上传脚本，可以递归目录操作
'''

from ftplib import FTP
import os,sys,string,datetime,time,re
import socket
import pat_d1
import threading
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper


#logger
loghelper.init_logger("ftp", stream=True)
logger = loghelper.get_logger("ftp")

dlist = []

class MYFTP:
    def __init__(self,rootdir_local,rootdir_local_o, hostaddr, username, password, remotedir, dirs_downloads, port=21, maxfiles=20):
        self.hostaddr = hostaddr
        self.username = username
        self.password = password
        self.remotedir = remotedir
        self.port = port
        self.ftp = FTP()
        self.rootdir_local = rootdir_local
        self.rootdir_local_o = rootdir_local_o
        self.dirs_downloads = dirs_downloads
        self.downloadlist = []
        self.maxf = maxfiles

    def login(self):
        try:
            # self.ftp.set_debuglevel(2)
            self.ftp.set_pasv(True)
            self.ftp.connect(self.hostaddr)
            logger.info("成功连接到 %s", self.hostaddr)
            self.ftp.login(self.username, self.password)
            logger.info("成功登录到 %s",self.hostaddr)
        except Exception, e:
            logger.info("登录失败")
            logger.info(e)
            self.ftp.close()
        try:
            self.ftp.cwd(self.remotedir)
        except Exception:
            logger.info("切换目录失败")
            self.ftp.close()

    def encode(self,code):
        self.ftp.encoding = code


    def get_dlist(self):
        dir_res = []
        self.ftp.dir('.', dir_res.append)

        dirs = [f.split(None, 8)[-1] for f in dir_res if f.startswith('d') and f.split(None, 8)[-1] not in ['.','..']]
        for dir in dirs:
            # logger.info(dir)
            if dir.decode('GB2312').strip() in self.dirs_downloads:
                localdir = dir.decode('GB2312').strip()
                self.walk(dir, localdir)
            self.ftp.cwd("/")

            if len(self.downloadlist) >= self.maxf:
                break

        self.ftp.quit()
        return self.downloadlist

    def is_same_size(self, localfile, remotefile):
        try:
            remotefile_size = self.ftp.size(remotefile)
        except:
            remotefile_size = -1
        try:
            localfile_size = os.path.getsize(localfile)
        except:
            localfile_size = -1
        logger.info('lo:%d  re:%d' , localfile_size, remotefile_size )
        if remotefile_size == localfile_size:
            return 1
        else:
            return 0

    def get_dirs_files(self):

        dir_res = []
        self.ftp.dir('.', dir_res.append)
        files = [f.split(None, 8)[-1] for f in dir_res if f.startswith('-')]
        dirs = [f.split(None, 8)[-1] for f in dir_res if f.startswith('d') and f.split(None, 8)[-1] not in ['.','..']]
        return (files, dirs)

    def add_to_dlist(self, localfile, remotefile, remotedir):
        if self.is_same_size(localfile, remotefile):
            logger.info('%s 文件大小相同，无需下载', localfile)
            return
        else:
            logger.info('>>>>>>>>>>>>下载文件 %s ... ...' , localfile)
            # return
        logger.info("Download from: %s", os.path.join(remotedir,remotefile))
        logger.info("Download to :%s", localfile)
        self.downloadlist.append({"remote": os.path.join(remotedir,remotefile),
                                  "local": localfile})

    def walk(self, downloaddir, localdir):
        if len(self.downloadlist) >= self.maxf:
            return
        logger.info('Walking to %s', downloaddir)
        self.ftp.cwd(downloaddir)
        local_dir =os.path.join(self.rootdir_local, localdir)
        local_dir_original = os.path.join(self.rootdir_local_o, localdir)
        # logger.info(localdir)
        if os.path.isdir(local_dir_original) and re.search("/\d{8}", local_dir):
            logger.info("%s is in %s", local_dir_original, self.rootdir_local_o)
            return
        try:
            os.mkdir(local_dir)
        except OSError:
            pass
        files, dirs = self.get_dirs_files()
        for f in files:
            file_local_dir = os.path.join(local_dir, f)
            logger.info("filename: %s",file_local_dir)
            self.add_to_dlist(file_local_dir,f, downloaddir)
            if len(self.downloadlist) >= self.maxf:
                return
        for d in dirs:
            nextdowndir = os.path.join(downloaddir,d)
            self.ftp.cwd("/")
            self.walk(nextdowndir,os.path.join(localdir, d.decode("GB2312")))


def download_file():
    while True:
        if len(dlist) == 0:
            return
        hostaddr = 'patdata1ftp.sipo.gov.cn'  # ftp地址
        username = 'cbs_xiniudata'  # 用户名
        password = '13LhYB'  # 密码
        port = 21
        obj = pat_d1.PyFTPclient(hostaddr, port, username, password)
        df = dlist.pop()
        obj.DownloadFile(df["remote"], df["local"])

if __name__ == '__main__':

    hostaddr = 'patdata1ftp.sipo.gov.cn' # ftp地址
    username = 'cbs_xiniudata' # 用户名
    password = '13LhYB' # 密码
    port = 21
    # rootdir_local  = '/Users/mac/git/tshbao/data/spider2/crawler/patdata/' # 本地目录
    rootdir_local = '/data2/patdata/'
    rootdir_local_o = '/data/patdata/'
    rootdir_remote = '/'          # 远程目录
    dirs_downloads_all = [
                      'CN-TXTS-10-A_中国发明专利申请公布标准化全文文本数据',
                      'CN-TXTS-10-B_中国发明专利授权公告标准化全文文本数据',
                      'CN-TXTS-20-U_中国实用新型专利授权公告标准化全文文本数据'
                      ]
    # dlist = []
    while True:
        for dir in dirs_downloads_all:
            while True:
                f = MYFTP(rootdir_local,rootdir_local_o,hostaddr, username, password, rootdir_remote, [dir], port)
                f.login()
                f.encode('GB2312')
                dlist = f.get_dlist()
                logger.info(dlist)
                break
            # for i in xrange(2):
            #     # obj = pat_d1.PyFTPclient(hostaddr, port, username, password)
            #     # obj.DownloadFile(df["remote"], df["local"])
            #     t = threading.Thread(target=download_file)
            #     t.start()
            for df in dlist:
                # if df["local"].find("20160817-4-001") == -1:
                #     continue
                obj = pat_d1.PyFTPclient(hostaddr, port, username, password)
                obj.DownloadFile(df["remote"], df["local"])

            # if len(dlist) < 10:
            #     break