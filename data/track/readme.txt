2018.7.4
机构版追踪功能

1. 创建或删除分组时
topic: track_conf
消息内容
    type: track_group
    action: create | delete
    id: track_group.id


2. 分组中增加或删除人员时
topic: track_conf
消息内容
    type: track_group_user_rel
    action: create | delete
    id: track_group_user_rel.id


3. 分组中增加或删除公司时
topic: track_conf
消息内容
    type: track_group_item_rel
    action: create | delete
    id: track_group_item_rel.id


4. 分组的追踪维度发生变化时
topic: track_conf
消息内容
    type: track_group_dimension
    action: create | delete
    id: track_group_dimension.id


5. 有消息时
   create | delete

6. 60秒内遗漏消息处理
7. 失效消息处理



8. 批量导入
topic: track_conf
消息内容
    type: track_import
    action: create
    id: track_import.id