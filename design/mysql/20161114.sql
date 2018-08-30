#mongodb
db: company
table: funding_news
column
    date    #新闻发布时间
    title
    link
    funding_id
    createTime
    createUser
    modifyTime
    modifyUser


#报错
#mongodb
db: company
table: correct


alter table collection add subType int default null after type;
alter table collection add index (subType);
alter table funding add tracked char(1) default null;
alter table funding add index (tracked);

alter table collection add picture varchar(50) default null;

update collection set name='最新获投公司' where id=157;
update collection set name='精选FA项目' where id=20;

alter table collection add wechatName varchar(200) default null;
alter table collection add wechatDesc text default null;
alter table collection add wechatPic varchar(50) default null;

update collection set wechatName='独家 |听说你刚刚错过戈壁VC Day？',
wechatDesc="立即查看过去三小时你错过的好项目" where id=974;

update collection set picture="583440284877af55fd34da84" where id=974;
