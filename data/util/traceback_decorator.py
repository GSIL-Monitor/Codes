# -*- coding: utf-8 -*-
import json
import re,time
import os,sys,traceback
import datetime
import db
import email_helper
import util
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import email_helper,util

def try_except(f):
    def handle_problems(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except Exception:
            exc_type, exc_instance, exc_traceback = sys.exc_info()
            formatted_traceback = ''.join(traceback.format_tb(exc_traceback))
            message = '\n{0}\n{1}:\n{2}'.format(
                formatted_traceback,
                exc_type.__name__,
                exc_instance
            )
            e_type = exc_type.__name__
            e_value = str(exc_instance)
            e_msg = "<html>" + message.replace('\n','<br>') + "</html>"
            check = 'N'
            file = traceback.format_tb(exc_traceback)[1].strip()
            e_files = re.search('File "(.*?)", line', file)
            e_file = ''
            if e_files:
                e_file = e_files.group(1)
            func = traceback.format_tb(exc_traceback)[-1].strip()
            e_func = func.split(',')[-1].replace('\n', '')
            item = {
                'type': e_type,
                'value': e_value,
                'msg': e_msg,
                'file': e_file,
                'func': e_func,
                'check': check,
                'createtime': datetime.datetime.now(),
                'modifytime': datetime.datetime.now()
            }
            print(json.dumps(item,ensure_ascii=False,indent=2,cls=util.CJsonEncoder))
            save_error_info(item)
#           raise exc_type(message)
#             print(exc_type(message)) # 异常的全部信息
#             print(len(traceback.format_tb(exc_traceback))) # 列表呈现的异常详情
#             print(exc_type.__name__) # 异常类型
#             print(exc_instance)  # 异常值
        finally:
            pass
        return f
    return handle_problems


def save_error_info(collection_content):
    mongo = db.connect_mongo()
    collection = mongo.raw.exc_info
    try:
        e_type = collection_content['type']
        e_value = collection_content['value']
        e_file = collection_content['file']
        check = collection_content['check']
        item = collection.find_one({'type':e_type,'value':e_value,'file':e_file,'check':check})
        if item is None:
            collection.insert_one(collection_content)
            print('insert exception info to exc_info done')
    except Exception as e:
        print('mongo error:%s'%e)
    mongo.close()


def send():
    while True:
        mongo = db.connect_mongo()
        collection = mongo.raw.exc_info
        items = list(collection.find({'check': 'N'}))
        mongo.close()
        if len(items) == 0:
            return
        for item in items:
            # "from_alias, reply_alias, reply_email, to, subject, content"
            collection.update({'type':item['type'],'value':item['value'],'file':item['file'],'check':'N'},{'$set':{'check':'Y','modifytime':datetime.datetime.now()}})
            from_alias = 'Hush'
            reply_alias = 'Hush'
            reply_email = "hush_guo@163.com"
            to = 'hush@xiniudata.com;bamy@xiniudata.com;arthur@xiniudata.com'
            subject = item['type']
            content = item['msg']
            email_helper.send_mail(from_alias,reply_alias,reply_email,to,subject,content)
        # time.sleep(60 * 60 * 12)

if __name__ == '__main__':
    send()












