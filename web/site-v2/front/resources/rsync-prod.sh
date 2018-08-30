#!/usr/bin/env bash
lessc less/style.less css/style.css
lessc less/style-admin.less  css/admin.css
lessc less/style-mobile.less  css/mobile.css
lessc less/style-search.less  css/search.css

rsync -vzrtopg --exclude less --exclude .DS_Store --progress -e ssh --delete ./ root@tshbao-web-01:/var/www/tsb2/front/resources
