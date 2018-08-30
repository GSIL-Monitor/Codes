#!/usr/bin/env bash
lessc public/less/style.less public/css/style.css

rsync -vzrtopg --exclude less --exclude .DS_Store --progress -e ssh --delete ../h5/ root@tshbao-task-02:/var/www/tsb2/h5
