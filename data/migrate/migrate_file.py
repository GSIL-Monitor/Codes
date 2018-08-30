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


def save_oss2_image(grid_id):
    if grid_id is None or grid_id.strip() == "":
        return

    item = mongo.temp.gridid.find_one({"gridid": grid_id})
    if item is not None:
        return

    out = grid.get(ObjectId(grid_id))
    logger.info(out.name)
    img, xsize, ysize = util.convert_image(out, out.name)
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


def migrate(type, table_name, column_name, _id=0):
    logger.info("migrate %s.%s from %s", table_name, column_name, _id)
    while True:
        conn = db.connect_torndb()
        items = conn.query("select id, " + column_name + " from " + table_name + " where id>%s order by id limit 100", _id)
        conn.close()

        for item in items:
            _id = item["id"]
            logger.info("%s.%s %s, %s", table_name, column_name, item["id"], item[column_name])
            logo_id = item[column_name]
            if type == "image":
                save_oss2_image(logo_id)
            elif type == "file":
                save_oss2_file(logo_id)
            #exit()

        if len(items) == 0:
            break
    logger.info("End.")


if __name__ == "__main__":
    '''
    | company | logo |
    | corporate | logo |
    | deal | logo |
    | investor | logo |
    | investor_member | logo | (无数据)
    | organization | logo |
    | source_company | logo |
    | source_investor | logo |
    | source_investor_member | logo | (无数据)
    | test_company | logo |  (无数据)
    | topic | logo |
    
    | contest_company_file | file        |  58352f2b4877af4060c6e389/云上会.pdf 
    | deal_file            | fileId      |
    | investor_chart       | file        |  (作废)
    | sourcedeal_file      | fileId      |

    | collection                 | picture          |
    | collection                 | wechatPic        |
    
    | deal_member      | photo       |
    | member           | photo       |
    | source_cf_member | photo       |  (无数据)
    | source_member    | photo       |
    | test_member      | photo       |  (无数据)
    '''

    images = [
        # ('organization', 'logo', 0),
        # ('topic', 'logo', 0),
        # ('collection', 'picture', 0),
        # ('collection', 'wechatPic', 0),
        # ('source_company', 'logo', 0),
        # ('source_investor', 'logo', 0),
        # ('source_member', 'photo', 0),
        # ('company', 'logo', 0),
        # ('corporate', 'logo', 0),
        # ('investor', 'logo', 0),
        # ('member', 'photo', 0),
        # ('deal', 'logo', 0),
        # ('deal_member', 'photo', 0),
        ('topic', 'background', 0)
    ]

    files = [
        # ("deal_file", "fileId", 0),
        # ("sourcedeal_file", "fileId", 0),
    ]

    for img in images:
        t_name, c_name, _id = img
        migrate("image", t_name, c_name, _id)

    for f in files:
        t_name, c_name, _id = f
        migrate("file", t_name, c_name, _id)