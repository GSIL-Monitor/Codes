import sys
import time
import oss2
import config
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")

class Oss2Helper:
    def __init__(self, _bucket_name=None):
        access_key_id, access_key_secret, endpoint, bucket_name = config.get_oss2_config()
        self.oss2_auth = oss2.Auth(access_key_id, access_key_secret)
        if _bucket_name is not None:
            bucket_name = _bucket_name
        self.oss2_bucket = oss2.Bucket(self.oss2_auth, endpoint, bucket_name)

    def put(self, file_name, data, headers={}):
        # data: bytes, str or file-like object
        cnt = 0
        while True:
            try:
                return self.oss2_bucket.put_object(file_name, data, headers=headers)
            except:
                traceback.print_exc()
                time.sleep(10)
                print "wrong number"
                print cnt
            cnt += 1
            if cnt > 3:
                raise Exception()

    def get(self, file_name):
        try:
            remote_stream = self.oss2_bucket.get_object(file_name)
            # remote_stream.read()
            return remote_stream
        except oss2.exceptions.NoSuchKey:
            return None
        except:
            raise

    def exists(self, file_name):
        return self.oss2_bucket.object_exists(file_name)
