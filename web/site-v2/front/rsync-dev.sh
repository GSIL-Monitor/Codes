#!/usr/bin/env bash
rm -rf output/*/public
lessc resources/less/style.less resources/css/style.css
lessc resources/less/style-admin.less  resources/css/admin.css
lessc resources/less/style-mobile.less  resources/css/mobile.css
lessc resources/less/style-search.less  resources/css/search.css

webpack --config webapp-site/webpack.config.js
webpack --config webapp-search/webpack.config.js
webpack --config webapp-user/webpack.config.js
webpack --config webapp-admin/webpack.config.js
webpack --config mobile-site/webpack.config.js
rsync -vzrtopg --exclude less --exclude .DS_Store --progress -e ssh --delete resources/ root@tshbao-task-02:/var/www/tsb2/front/resources
rsync -vzrtopg --exclude js --exclude node_modules --exclude package.json --exclude .DS_Store --progress -e ssh --delete output/ root@tshbao-task-02:/var/www/tsb2/front/output
