[program:parser_next2]
command=/opt/py-env/bin/python next_parser.py
directory=/data/task-v2/spider2/parser/next
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/data/task-v2/spider2/parser/next/logs/next.log


[program:parser_toutiao_news2]
command=/opt/py-env/bin/python toutiao_news_parser.py
directory=/data/task-v2/spider2/parser/news
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/data/task-v2/spider2/parser/news/logs/toutiao_news_parser.log