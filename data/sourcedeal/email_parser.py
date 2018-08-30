# -*- coding: utf-8 -*-

from email.Header import decode_header
import email
from email.utils import parseaddr,parsedate
from StringIO import StringIO
from datetime import datetime

class NotSupportedMailFormat(Exception):
    pass


def parse_attachment(message_part):
    content_disposition = message_part.get("Content-Disposition", None)
    if content_disposition:
        #print content_disposition
        dispositions = content_disposition.strip().split(";")
        if bool(content_disposition and dispositions[0].lower() == "attachment") or bool(content_disposition and dispositions[0].lower() == "inline"):

            file_data = message_part.get_payload(decode=True)
            # Used a StringIO object since PIL didn't seem to recognize
            # images using a custom file-like object
            attachment = StringIO(file_data)
            attachment.content_type = message_part.get_content_type()
            attachment.size = len(file_data)
            attachment.name = None
            attachment.create_date = None
            attachment.mod_date = None
            attachment.read_date = None
            
            for param in dispositions[1:]:
                param = param.strip()
                name,value = param.split("=",1)
                name = name.lower()

                if name == "filename":
                    h = email.Header.Header(value.lstrip('"').rstrip('"'))
                    dh = email.Header.decode_header(h)
                    fname = dh[0][0]
                    if dh[0][1] != None:
                        fname = fname.decode(dh[0][1])
                    attachment.name = fname
                    #print fname
                elif name == "create-date":
                    attachment.create_date = value  #TODO: datetime
                elif name == "modification-date":
                    attachment.mod_date = value #TODO: datetime
                elif name == "read-date":
                    attachment.read_date = value #TODO: datetime
            return attachment

    return None
 
def parse(content):
    """
    Parse the email and return a dictionary of relevant data.
    """
    #p = EmailParser()
    #msgobj = p.parse(content)
    msgobj = content
    if msgobj['Subject'] is not None:
        decodefrag = decode_header(msgobj['Subject'])
        subj_fragments = []
        for s , enc in decodefrag:
            if enc:
                s = unicode(s , enc).encode('utf8','replace')
            subj_fragments.append(s)
        subject = ''.join(subj_fragments)
    else:
        subject = None

    attachments = []
    body = None 
    html = None 
    for part in msgobj.walk():
        #print "*****************"
        #print part
        attachment = parse_attachment(part)
        if attachment:
            #print part
            strtemp = part.get_filename()
            if strtemp is not None:
                strtemp = strtemp.lstrip('"').rstrip('"')
            h = email.Header.Header(strtemp)
            dh = email.Header.decode_header(h)
            fname = dh[0][0]
            if dh[0][1] != None:
                fname = fname.decode(dh[0][1])
            attachment.name = fname
            attachments.append(attachment)
        if part.get_content_type() == "text/plain":
            if body is None:
                body = ""
            body += unicode(
                part.get_payload(decode=True),
                part.get_content_charset(),
                'replace'
            ).encode('utf8','replace')
        elif part.get_content_type() == "text/html":
            if html is None:
                html = ""
            html += unicode(
                part.get_payload(decode=True),
                part.get_content_charset(),
                'replace'
            ).encode('utf8','replace')
    
    cc = None
    if msgobj.has_key('Cc'):
        #print getaddresses(msgobj.get_all('Cc',[]))
        cc = parseaddr(msgobj.get('Cc'))[1]
    return {
        'subject' : subject,
        'body' : body,
        'html' : html,
        'from' : parseaddr(msgobj.get('From'))[1], # Leave off the name and only return the address
        'to' : parseaddr(msgobj.get('To'))[1], # Leave off the name and only return the address
        'cc' : cc,
        'attachments': attachments,
        'date': datetime(*parsedate(msgobj["Date"])[0:6])
    }