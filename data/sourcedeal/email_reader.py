# -*- coding: utf-8 -*-

import imaplib
import email
import email_parser
import traceback

def connect(IMAP_SERVER, IMAP_PORT, username, password):
    while True:
        try:
            M = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
            #M.debug = 4
            M.login(username, password)
            M.select()
            return M
        except:
            try:
                M.logout()
            except:
                pass

def receive(IMAP_SERVER, IMAP_PORT, username, password, one=False):
    raw_msgs = []
    msgs = []

    while True:
        flag = False
        M = connect(IMAP_SERVER, IMAP_PORT, username, password)
        #print "connected"
        typ, data = M.search(None, 'UNSEEN')
        #typ, data = M.search(None, 'ALL')
        #print "searched"
        mids = data[0].split()
        if len(mids) == 0:
            break
        for mid in mids:
            try:
                status, response = M.fetch(mid,"(RFC822)")
                try:
                    M.store(mid, '+FLAGS', '\\SEEN')
                except Exception,x:
                    traceback.print_exc()
                    m = connect(IMAP_SERVER, IMAP_PORT, username, password)
                    m.store(mid, '+FLAGS', '\\SEEN')
                    m.logout()

                mailText = response[0][1]
                #print mailText
                mail_message = email.message_from_string(mailText)
                raw_msgs.append(mail_message)
                flag = True
            except Exception,x:
                traceback.print_exc()
            if one:
                break
        try:
            #M.close()    #QQ error!
            M.logout()
        except Exception,x:
            traceback.print_exc()

        if flag:
            break

    for mail_message in raw_msgs:
        msg = email_parser.parse(mail_message)
        #print msg["subject"]
        # print msg["from"]
        # print msg["to"]
        # print msg["body"]
        # print msg["html"]
        msgs.append(msg)

    return msgs


if __name__ == '__main__':
    msgs = receive("imap.exmail.qq.com", 993,"coldcall@gobi.com.cn", "gbkr0419", one=True)
    if len(msgs) > 0:
        print msgs[0]
