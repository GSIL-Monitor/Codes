mvn package -Dmaven.test.skip=true
rsync -vzrtopg --exclude WEB-INF/classes --progress -e ssh --delete api-user/target/api-user/  root@tshbao-task-02:/var/www/tsb2/api/api-user
rsync -vzrtopg --exclude WEB-INF/classes --progress -e ssh --delete api-company/target/api-company/  root@tshbao-task-02:/var/www/tsb2/api/api-company
rsync -vzrtopg --exclude WEB-INF/classes --progress -e ssh --delete api-admin/target/api-admin/  root@tshbao-task-02:/var/www/tsb2/api/api-admin