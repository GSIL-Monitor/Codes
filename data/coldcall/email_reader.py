# -*- coding: utf-8 -*-

import imaplib
import email
import email_parser
import traceback

def receive(IMAP_SERVER, IMAP_PORT, username, password):
    msgs = []
    
    M = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT) 
    #M.debug = 4
    M.login(username, password)
    M.select()
    typ, data = M.search(None, 'UNSEEN')
    #typ, data = M.search(None, 'ALL')
    
    for mid in data[0].split():
        #print mid
        try:
            status, response = M.fetch(mid,"(RFC822)")
            M.store(mid, '+FLAGS', '\\SEEN')
            mailText = response[0][1]
            #print mailText
            mail_message = email.message_from_string(mailText)
    
            msg = email_parser.parse(mail_message)
            #print msg["subject"]
            #print msg["from"]
            #print msg["to"]
            #print msg["body"]
            #print msg["html"]
            msgs.append(msg)
        except Exception,x:
            traceback.print_exc()
    
    try:
        #M.close()    #QQ error!
        M.logout()
    except Exception,x:
        print x
        traceback.print_exc()

    return msgs