# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
reload(sys)
sys.setdefaultencoding('utf-8')


import smtplib
from email.mime.text import MIMEText


server = {
    'server': 'smtp.mxhichina.com',
    'port': 25,
    'user': 'm.daniel@xiniudata.com',
    'password': 'Gbkr0419'
}


def send_mail(receivers, subject, text):

    global server

    # text = u'本周处理'
    sender = u'm.daniel@xiniudata.com'
    # receivers = ['victor@xiniudata.com']
    # subject = u'Test'

    msg = MIMEText(text, _charset='utf-8')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ','.join(receivers)

    s = smtplib.SMTP()
    s.connect(server.get('server'), server.get('port'))
    s.login(server.get('user'), server.get('password'))
    s.sendmail(sender, receivers, msg.as_string())
    s.quit()


if __name__ == '__main__':

    print __file__

    send_mail(['victor@xiniudata.com'], u'test', u'test')