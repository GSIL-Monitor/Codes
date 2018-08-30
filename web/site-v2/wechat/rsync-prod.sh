#!/usr/bin/env bash
rsync -vzrtopg --exclude *.sh --exclude *.txt --exclude .DS_Store --progress -e ssh --delete . root@tshbao-web-01:/var/www/tsb2/wechat
