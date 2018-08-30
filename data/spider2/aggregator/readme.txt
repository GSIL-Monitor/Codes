1.beian 备案查询
2.tianyancha 工商查询
3.公司名规范化， url规范 -> domain
4.交叉对比： 工商/股东信息/Member

网站meta, alexa, artifact验证
beian
工商 member

匹配： 1.full_name 2.domain 3.company_name/artifact_name 相同->进入候选
信息合并：根据源，进行投票；优先级：website(提取title，根据alexa排序)、36kr、ITjuzi ...
人工修改过的字段，不改变
establishDate，若为空/不规范，使用工商创立时间。


[program:beian2]
command=/opt/py-env/bin/python beian.py
directory=/data/task-v2/spider2/aggregator/beian
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/data/task-v2/spider2/aggregator/beian/logs/beian.log


[program:company_aggregator2]
command=/opt/py-env/bin/python company_aggregator.py
directory=/data/task-v2/spider2/aggregator/company
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/data/task-v2/spider2/aggregator/company/logs/company_aggregator.log

[program:collection2]
command=/opt/py-env/bin/python run_collection.py
directory=/data/task-v2/spider2/aggregator/collection
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/data/task-v2/spider2/aggregator/collection/logs/collection.log


[program:news_aggregator2]
command=/opt/py-env/bin/python news_aggregator.py
directory=/data/task-v2/spider2/aggregator/news
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/data/task-v2/spider2/aggregator/news/logs/news_aggregator.log