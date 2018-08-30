pip install gevent



[program:crawler_next2]
command=/opt/py-env/bin/python run_next.py
directory=/data/task-v2/spider2/crawler/next
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/data/task-v2/spider2/crawler/next/logs/next.log


[program:migrate_news]
command=/opt/py-env/bin/python migrate.py
directory=/data/task-v2/spider2/crawler/news
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/data/task-v2/spider2/crawler/news/logs/migrate_news.log


[program:crawler_toutiao_news2]
command=/opt/py-env/bin/python toutiao_news.py 2 1
directory=/data/task-v2/spider2/crawler/news
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/data/task-v2/spider2/crawler/news/logs/toutiao_news.log