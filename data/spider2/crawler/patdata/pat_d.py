#coding=utf-8
import ftplib


ftp = ftplib.FTP()

hostaddr = 'patdata1ftp.sipo.gov.cn' # ftp地址
username = 'cbs_xiniudata' # 用户名
password = '13LhYB' # 密码
port = 21

folder = '/CN-TXTS-10-A_中国发明专利申请公布标准化全文文本数据/20160817/'
folder2 = folder.decode('utf-8').encode("GB2312")
print folder2
ftp.connect(host=hostaddr, port=port)
ftp.login(user=username, passwd=password)
#ftp.prot_p()
ftp.cwd(folder2)

dir_res = []
ftp.dir('.', dir_res.append)
# print dir_res

for file in ftp.nlst():
    print file
    f = open(file, "w+b")
    ftp.retrbinary('RETR %s' % file, callback=f.write, blocksize=8192)
    f.close()