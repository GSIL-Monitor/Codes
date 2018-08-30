#!/usr/bin/env bash
rm -rf ../output/mobile/public
lessc ../resources/less/style-mobile.less  ../resources/css/mobile.css
webpack
rsync -vzrtopg --exclude less --exclude .DS_Store --progress -e ssh --delete ../resources/ root@tshbao-web-01:/var/www/tsb2/front/resources
rsync -vzrtopg --exclude js --exclude node_modules --exclude package.json --exclude .DS_Store --progress -e ssh --delete ../output/ root@tshbao-web-01:/var/www/tsb2/front/output
