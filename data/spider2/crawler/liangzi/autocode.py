# -*- coding=utf-8 -*-

import base64
import random


def now():
    import time
    return int(time.time())

def md5(s):
    try:
        from hashlib import md5
    except ImportError:
        from md5 import md5
    return md5(s).hexdigest()   
def b64_encode(s):
    return base64.encodestring(s)
    
def b64_decode(s):
    try:
        return base64.decodestring(s)
    except:
        return b64_decode(s+"=")

def random_string(length):
    charArray = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    return ''.join([random.choice(charArray) for i in range(length)])

class Authcode(object):
    ENCODE, DECODE = 0, 1

    @classmethod
    def random(cls,length):
        return random_string(length);
    @classmethod
    def quantum_encode(cls, string, key, expiry=0):
        return cls.authcode(string, key, cls.ENCODE, expiry)

    @classmethod
    def quantum_decode(cls, string, key, expiry=0):
        return cls.authcode(string, key, cls.DECODE, expiry)

    @classmethod
    def authcode(cls, string, key, operation, expiry=0):
        if not string:
            return ''
        
        ckey_length = 4
        keya = md5(key[:16])
        keyb = md5(key[16:][:16])
        if ckey_length:
            if operation == cls.DECODE:
                keyc = string[:ckey_length]
            else:
                keyc = random_string(ckey_length)
        else:
            keyc = ''

        cryptkey = keya + md5(keya + keyc)
        key_length = len(cryptkey)

        time_=''
        if operation == cls.DECODE:
            string = b64_decode(string[ckey_length:])
        else:
            if expiry > 0:
                expiry += now()
                time_ = '%10d' % expiry
            else:
                time_ = '0000000000'
            string = time_ + md5(string + keyb)[:16] + string
        string_length = len(string)

        result = ''
        rndkey = [ord(cryptkey[i % key_length]) for i in range(256)]
        box = range(256)
        j = 0
        for i in xrange(256):
            j = (j + box[i] + rndkey[i]) % 256
            tmp = box[i]
            box[i] = box[j]
            box[j]=tmp
            

        a, j = 0, 0
        for i in xrange(string_length):
            a = (a + 1) % 256
            j = (j + box[a]) % 256
            tmp = box[a]
            box[a] = box[j]
            box[j]=tmp
            
            result += chr(ord(string[i]) ^ (box[(box[a] + box[j]) % 256]))

        if operation == cls.DECODE:
            if (result[:10] == "0000000000" or int(result[:10]) - now() > 0) \
                and result[10:26] == md5(result[26:] + keyb)[:16]:
                    return result[26:]
            else:
                return ''
        else:
            return keyc + b64_encode(result).replace('=', '')
