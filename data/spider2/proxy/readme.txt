[program:proxy2]
command=/opt/py-env/bin/python proxy.py
directory=/data/task-v2/spider2/proxy
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/data/task-v2/spider2/proxy/logs/proxy.log