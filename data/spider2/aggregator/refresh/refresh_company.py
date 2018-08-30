# -*- coding: utf-8 -*-
import os, sys, datetime, random
import time

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db,name_helper, email_helper


sentenes = [
    "人生是一条没有回程的单行线，上帝不会给你一张返程的票。",
    "对待生活中的每一天若都像生命中的最后一天去对待，人生定会更精彩。",
    "活在昨天的人失去过去，活在明天的人失去未来，活在今天的人拥有过去和未来。",
    "如果我们都去做自己能力做得到的事，我们会让自己大吃一惊。",
    "出路出路，走出去了，总是会有路的。困难苦难，困在家里就是难。",
    "学的到东西的事情是锻炼，学不到的是磨练。",
    "背负着过去的痛苦，夹杂着现实的烦恼，这对于人的心灵而言是无任何益处。",
    "坚持最难，但成果也最大。",
    "只有你学会把自己已有的成绩都归零，才能腾出空间去接纳更多的新东西，如此才能使自己不断的超越自己。",
    "人之所以痛苦，在于追求错误的东西。",
    "与其说是别人让你痛苦，不如说自己的修养不够。",
    "生活是一面镜子。你对它笑，它就对你笑；你对它哭，它也对你哭。",
    "只有不断找寻机会的人才会及时把握机会。",
    "做一个决定，并不难，难的是付诸行动，并且坚持到底。",
    "忍别人所不能忍的痛，吃别人所别人所不能吃的苦，是为了收获得不到的收获。",
    "过错是暂时的遗憾，而错过则是永远的遗憾！",
    "环境不会改变，解决之道在于改变自己。",
    "勇气是控制恐惧心理，而不是心里毫无恐惧。",
    "还能冲动，表示你还对生活有激情，总是冲动，表示你还不懂生活。",
    "如果你不给自己烦恼，别人也永远不可能给你烦恼，烦恼都是自己内心制造的。",
    "好好管教自己，不要管别人。",
    "你硬要把单纯的事情看得很严重，那样子你会很痛苦。",
    "如果你能像看别人缺点一样，如此准确的发现自己的缺点，那么你的生命将会不平凡。",
    "无论你觉得自己多么的了不起，也永远有人比你更强；无论你觉得自己多么的不幸，永远有人比你更加不幸。",
    "大部分人往往对已经失去的机遇捶胸顿足，却对眼前的机遇熟视无睹。",
    "放弃谁都可以，千万不要放弃自己！",
    "人生是一场旅行，在乎的不是目的地，是沿途的风景以及看风景的心情。",
    "再长的路，一步步也能走完，再短的路，不迈开双脚也无法到达。",
    "多一分心力去注意别人，就少一分心力反省自己。",
    "人生就像钟表，可以回到起点，却已不是昨天！",
    "人生就像弈棋，一步失误，全盘皆输。",
    "在必要时候需要弯一弯，转一转，因为太坚强容易折断，我们需要更多的柔软，才能战胜挫折。",
    "自以为拥有财富的人，其实是被财富所拥有。",
    "人生就像一个动物园，当你以为你在看别人耍猴的时候，却不知自己也是猴子中的一员！",
    "从绝望中寻找希望，人生终将辉煌。",
    "你不能左右天气，但可以改变心情。你不能改变容貌，但可以掌握自己。你不能预见明天，但可以珍惜今天。",
    "尝试去把别人拍过来的砖砌成结实的地基，生活就不会那么辛苦了。",
    "一个懒惰的少年将来就是一褴褛的老人。",
    "在实现理想的路途中，必须排除一切干扰，特别是要看清那些美丽的诱惑。",
    "活着一天，就是有福气，就该珍惜。当我哭泣我没有鞋子穿的时候，我发现有人却没有脚。",
    "人生是个圆，有的人走了一辈子也没有走出命运画出的圆圈，其实，圆上的每一个点都有一条腾飞的切线。",
    "我们心中的恐惧，永远比真正的危险巨大的多。",
    "命运掌握在自己手中。要么你驾驭生命，要么生命驾驭你，你的心态决定你是坐骑还是骑手。",
    "不要拿小人的错误来惩罚自己，不要在这些微不足道的事情上折磨浪费自己的宝贵时间。",
    "一杯清水因滴入一滴污水而变污浊，一杯污水却不会因一滴清水的存在而变清澈。",
    "运气就是机会碰巧撞到了你的努力。",
    "得之坦然，失之淡然，顺其自然，争其必然。",
    "时间是治疗心灵创伤的大师，但绝不是解决问题的高手。",
    "天道酬勤。也许你付出了不一定得到回报，但不付出一定得不到回报。",
    "逆境是成长必经的过程，能勇于接受逆境的人，生命就会日渐的茁壮。",
    "人一生下就会哭，笑是后来才学会的。所以忧伤是一种低级的本能，而快乐是一种更高级的能力。",
    "两个人共尝一个痛苦只有半个痛苦，两个人共享一个欢乐却有两个欢乐。",
    "放弃该放弃的是无奈，放弃不该放弃的是无能，不放弃该放弃的是无知，不放弃不该放弃的是执著！",
    "行动是治愈恐惧的良药，而犹豫",
    "你把周围的人看作魔鬼，你就生活在地狱；你把周围的人看作天使，你就生活在天堂。",
    "宁愿做过了后悔，也不要错过了后悔。",
    "困难是一块顽石，对于弱者它是绊脚石，对于强者它是垫脚石。",
    "笑对人生，能穿透迷雾；笑对人生，能坚持到底；笑对人生，能化解危机；笑对人生，能照亮黑暗。",
    "人生最大的悲哀不是失去太多，而是计较太多，这也是导致一个人不快乐的重要原因。",
    "我们总是对陌生人太客气，而对亲密的人太苛刻。",
    "人的一生就像一篇文章，只有经过多次精心修改，才能不断完善。摘自：读书名言",
    "虽然我们无法改变人生，但可以改变人生观。虽然我们无法改变环境，但我们可以改变心境。",
    "如果你还认为自己还年轻，还可以蹉跎岁月的话，你终将一事无成，老来叹息。",
    "当你快乐时，你要想，这快乐不是永恒的。当你痛苦时，你要想，这痛苦也不是永恒的。",
    "命运就像自己的掌纹，虽然弯弯曲曲，却永远掌握在自己手中。",
    "不要浪费你的生命，在你一定会后悔的地方上。",
    "激情，这是鼓满船帆的风。风有时会把船帆吹断；但没有风，帆船就不能航行。",
    "人是可以快乐地生活的，只是我们自己选择了复杂，选择了叹息！",
    "不管从什么时候开始，重要的是开始以后不要停止；不管在什么时候结束，重要的是结束以后不要后悔。",
    "抱最大的希望，为最大的努力，做最坏的打算。",
    "人生最大的错误是不断担心会犯错。",
    "忌妒别人，不会给自己增加任何的好处，忌妒别人，也不可能减少别人的成就。",
    "长得漂亮是优势，活得漂亮是本事。",
    "大多数人想要改造这个世界，但却罕有人想改造自己。",
    "每个人都有潜在的能量，只是很容易被习惯所掩盖，被时间所迷离，被惰性所消磨。",
    "积极的人在每一次忧患中都看到一个机会，而消极的人则在每个机会都看到某种忧患。",
    "创造机会的人是勇者，等待机会的人是愚者。",
    "旁观者的姓名永远爬不到比赛的计分板上。",
    "同样的瓶子，你为什么要装毒药呢？同样的心理，你为什么要充满着烦恼呢？",
    "行动不一定带来快乐，而无行动则决无快乐。",
    "你可以一无所有，但绝不能一无是处。",
    "突破心理障碍，才能超越自己。",
    "如果我们有着快乐的思想，我们就会快乐；如果我们有着凄惨的思想，我们就会凄惨。",
    "时光不回头，当下最重要。",
    "面对困境，悲观的人因为往往只看到事情消极一面。",
    "不要因为自己还年轻，用健康去换去金钱，等到老了，才明白金钱却换不来健康。",
    "你不要一直不满他人，你应该一直检讨自己才对。",
    "心念一转，万念皆转；心路一通，万路皆通。",
    "愚昧者怨天尤人，无能者长吁短叹，儒弱者颓然放弃。",
    "智者用无上心智和双手为自己开辟独有的天空，搭建生命的舞台。",
    "时间是小偷，他来时悄无声息，走后损失惨重，机会也是如此。",
    "成功的关键在于相信自己有成功的能力。",
    "人的缺点就像花园里的杂草，如果不及时清理，很快就会占领整座花园。",
    "滴水穿石不是靠力，而是因为不舍昼夜。",
    "相信自己能力的人，任何事情都能够做到。",
    "把事情办好的秘密就是行动。成功之路就是有条理思考之后的行动！行动！行动！",
    "人之所以有一张嘴，而有两只耳朵，原因是听的要比说的多一倍。",
    "哲人无忧，智者常乐。并不是因为所爱的一切他都拥有了，而是所拥有的一切他都爱。",
    "泪水和汗水的化学成分相似，但前者只能为你换来同情，后者却可以为你赢得成功。",
    "越是成熟的稻穗，越懂得弯腰。",
]
#logger
loghelper.init_logger("refresh_news", stream=True)
logger = loghelper.get_logger("refresh_news")

def patch_company_establish_date(company_id):
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    collection_gongshang = mongo.info.gongshang
    company1 = conn.get("select * from company where id=%s", company_id)
    establish_date = None
    if company1["corporateId"] is not None:

        corporate = conn.get("select * from corporate where id=%s", company1["corporateId"])
        if corporate is not None and corporate["fullName"] is not None:
            gongshang = collection_gongshang.find_one({"name": corporate["fullName"]})

            if gongshang is not None and gongshang.has_key("establishTime"):
                try:
                    if establish_date is None or (gongshang["establishTime"] is not None and gongshang["establishTime"] != establish_date):
                        establish_date = gongshang["establishTime"]
                except:
                    pass

        if establish_date is None:
            aliases = conn.query("select * from corporate_alias where "
                                 "(active is null or active !='N') and corporateId=%s", company1["corporateId"])
            for alias in aliases:
                gongshang = collection_gongshang.find_one({"name": alias["name"]})
                if gongshang is not None and gongshang.has_key("establishTime"):
                    try:
                        if establish_date is None or (gongshang["establishTime"] is not None and gongshang["establishTime"] != establish_date):
                            establish_date = gongshang["establishTime"]
                    except:
                        pass
                if establish_date is not None:
                    break

        if establish_date is not None:

            logger.info("Company: %s establishDate: %s", company_id, establish_date)
            try:
                conn.update("update corporate set establishDate=%s where id=%s", establish_date, company1["corporateId"])
            except:
                pass

        #patch round
        if corporate is not None:
            funding = conn.get("select * from funding where corporateId=%s and (active is null or active !='N') "
                               "order by fundingDate desc limit 1",
                               corporate["id"])
            if funding is not None:
                # corporate = conn.get("select * from corporate where id=%s", corporate_id)
                # if corporate is not None:
                conn.update("update corporate set round=%s where id=%s",
                            funding["round"],  corporate["id"])
            else:
                if corporate["round"] is not None:
                    conn.update("update corporate set round=-1 where id=%s", corporate["id"])
    conn.close()
    mongo.close()

def patch_company_location(company_id):
    conn = db.connect_torndb()
    company1 = conn.get("select * from company where id=%s", company_id)
    if company1["corporateId"] is not None:
        corporate = conn.get("select * from corporate where id=%s", company1["corporateId"])

        if corporate is not None and (corporate["locationId"] is None or corporate["locationId"] == 0):
            locationId = None

            alias0 = [{"name":corporate["fullName"]}] if corporate["fullName"] is not None else []
            aliases = conn.query("select * from corporate_alias where corporateId=%s and "
                                 "(active is null or active ='Y') and verify='Y'",
                                 company1["corporateId"])
            for alias in alias0+aliases:
                logger.info(alias["name"])
                loc1, loc2 = name_helper.get_location_from_company_name(alias["name"])
                logger.info("%s/%s",loc1,loc2)
                if loc1 is not None:
                    l = conn.get("select *from location where locationName=%s", loc1)
                    if l:
                        locationId = l["locationId"]
                        break
            if locationId is not None:
                conn.update("update corporate set locationId=%s where id=%s", locationId, company1["corporateId"])
    conn.close()

def gen_content(company_id, user_id):
    conn = db.connect_torndb()
    company = conn.get("select * from company where id=%s", company_id)
    user = conn.get("select * from user where id=%s", user_id)
    if user is None or user["email"] is None or user["email"].strip() == "":
        content = None
        touser = None
    else:
        # logger.info(company)
        # logger.info(user)
        # logger.info("%s,%s",user["name"],company["name"])
        ss = random.randint(0, len(sentenes) - 1)
        link = "http://pro.xiniudata.com/validator/#/company/%s/overview" % company["code"]
        content = '''<div>Dears, ''' + user["username"] + '''   <br /><br />

                Company ''' + company["name"] + '''已经完成拓展 <br /><br /><br />''' + link + '''<br /><br /><br />''' +sentenes[ss]+ '''</div>'''
        touser = user["email"]

    conn.close()
    return  content, touser

if __name__ == '__main__':
    checkColums = ["itjuzi","kr36", "gongshang", "artifact","news"]

    logger.info("python refresh_news")
    while True:
        conn = db.connect_torndb()
        mongo = db.connect_mongo()
        collection_raw = mongo.raw.projectdata
        collection = mongo.task.company_refresh

        tasks = list(collection.find({"status":0, "extendType":0}))
        for t in tasks:
            if t.has_key("subStatus") is True:
                fflag = True
                for cc in checkColums:
                    if t["subStatus"].has_key(cc) is True:
                        logger.info("Company %s finish : %s", t["companyId"], cc)
                    else:
                        logger.info("Company %s missing : %s", t["companyId"], cc)
                        fflag = False
                if fflag is False:
                    pass
                else:
                    logger.info("Company %s finish all \n\n", t["companyId"])
                    patch_company_establish_date(t["companyId"])
                    patch_company_location(t["companyId"])
                    collection.update_one({"_id": t["_id"]}, {"$set": {"status": 1,
                                                                       "finishTime": datetime.datetime.now() - datetime.timedelta(hours=8)}})
                    c, t = gen_content(t["companyId"], t["createUser"])
                    if c is not None and t is not None:
                        logger.info(c)
                        email_helper.send_mail("烯牛数据数据开发组", "烯牛数据数据开发组", "bamy@xiniudata.com",
                                               t, "拓展完毕通知", c)


        conn.close()
        mongo.close()
        time.sleep(30)

