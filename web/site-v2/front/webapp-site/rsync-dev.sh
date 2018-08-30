#!/usr/bin/env bash
rm -rf ../output/site/public
lessc ../resources/less/style.less  ../resources/css/style.css
webpack
rsync -vzrtopg --exclude less --exclude .DS_Store --progress -e ssh --delete ../resources/ root@tshbao-task-02:/var/www/tsb2/front/resources
rsync -vzrtopg --exclude js --exclude node_modules --exclude package.json --exclude .DS_Store --progress -e ssh --delete ../output/ root@tshbao-task-02:/var/www/tsb2/front/output
