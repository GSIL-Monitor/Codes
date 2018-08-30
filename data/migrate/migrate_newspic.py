# -*- coding: utf-8 -*-
# /opt/py-env/bin/pip install cairosvg==1.0.22
import os, sys
from gridfs import GridFS
from bson import ObjectId

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, util, oss2_helper

#logger
loghelper.init_logger("migrate_file", stream=True)
logger = loghelper.get_logger("migrate_file")

mongo = db.connect_mongo()
grid = GridFS(mongo.gridfs)
oss2 = oss2_helper.Oss2Helper()


def save_oss2_image(grid_id,size=None):
    if grid_id is None or grid_id.strip() == "":
        return

    item = mongo.temp.gridid.find_one({"gridid": grid_id})
    if item is not None:
        return

    out = grid.get(ObjectId(grid_id))
    logger.info("%s -> %s", grid_id, out.name)
    if size is None:
        img, xsize, ysize = util.convert_image(out, out.name)
    else:
        img, xsize, ysize = util.convert_image(out, out.name, size=size)
    headers = {"Content-Type": "image/jpeg"}
    oss2.put(grid_id, img, headers=headers)
    mongo.temp.gridid.insert({"gridid": grid_id})


def save_oss2_file(grid_id):
    if grid_id is None or grid_id.strip() == "":
        return

    item = mongo.temp.gridid.find_one({"gridid": grid_id})
    if item is not None:
        return

    out = grid.get(ObjectId(grid_id))
    logger.info(out.name)
    content_type = out.content_type
    headers = {"Content-Type": content_type}
    oss2.put(grid_id, out, headers=headers)
    mongo.temp.gridid.insert({"gridid": grid_id})


def migrate_image():
    newses = list(mongo.article.news.find({"source":{'$in':[13612,13613]}}))
    for news in newses:
        _id = news["_id"]
        if news.has_key("postId") is True and news["postId"] is not None and news["postId"] != "None":
            save_oss2_image(news["postId"])

        # if news.has_key("imgChecked") is True and news["imgChecked"] is True:
        #     continue
        # logger.info("%s, %s", _id, news.get("title","no title"))
        # if news.has_key("contents") is True and len(news["contents"]) > 0:
        #     try:
        #         aa = news["contents"][0]['content']
        #     except:
        #         news["contents"] = eval(news["contents"])
        #     for content in news["contents"]:
        #         if content.has_key("image") is True and content["image"] is not None and content["image"] != "None":
        #             if news.has_key("type") is True and news["type"] == 60006:
        #                 save_oss2_image(content["image"], size=1024)
        #             else:
        #                 save_oss2_image(content["image"])
        # mongo.article.news.update_one({"_id": _id}, {'$set':{"imgChecked": True}})
        # break

    logger.info("End.")


if __name__ == "__main__":

    migrate_image()
