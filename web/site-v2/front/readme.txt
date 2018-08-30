nginx
        install from
        http://openresty.org

        add the following in nginx.conf

server {
        listen       10.45.141.3:80;
        server_name  sedna2.gobivc.com;

        client_max_body_size 100m;


        location /resources {
            alias /var/www/tsb2/front/resources;
            expires -1;
        }

        location / {
            root /var/www/tsb2/front/output/site/public;
            index index.html index.htm;
            expires -1;
        }

        location /search {
            alias /var/www/tsb2/front/output/search/public;
            index index.html index.htm;
            expires -1;
        }

        location /user {
            alias /var/www/tsb2/front/output/user/public;
            index index.html index.htm;
            expires -1;
        }

        location /admin {
            alias /var/www/tsb2/front/output/admin/public;
            index index.html index.htm;
            expires -1;
        }

        location /mobile {
            alias /var/www/tsb2/front/output/mobile/public;
            index index.html index.htm;
            expires -1;
        }


        location /api/open/company {
            rewrite ^(.*)$ /api-company/$1 break;z
            proxy_set_header X-Real-IP $remote_addr;
            proxy_pass http://localhost:8080;
        }

        location /api/user/login {
            rewrite ^(.*)$ /api-user/$1 break;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_pass http://localhost:8080;
        }

        location /api/company/file {
            rewrite ^(.*)$ /api-company/$1 break;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_pass http://localhost:8080;
        }

        location /api/company {
            rewrite ^(.*)$ /api-user/api/user/access/identify?path=/api-company$1 break;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_pass http://localhost:8080;
        }

        location /api/user {
            rewrite ^(.*)$ /api-user/api/user/access/identify?path=/api-user$1 break;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_pass http://localhost:8080;
        }

	location /api/admin/proxy {
            rewrite ^(.*)$ /api-admin/$1 break;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_pass http://localhost:8080;
        }

        location /api/admin {
            rewrite ^(.*)$ /api-user/api/user/access/identify?path=/api-admin$1 break;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_pass http://localhost:8080;
        }

        location /api-company {
            internal;
            rewrite_by_lua '
                    ngx.req.set_method(ngx.HTTP_POST)
                    ngx.req.set_body_data(ngx.var.upstream_http_postbody)
                    ';
            proxy_pass http://localhost:8080;
        }

        location /api-user {
            internal;
            rewrite_by_lua '
                    ngx.req.set_method(ngx.HTTP_POST)
                    ngx.req.set_body_data(ngx.var.upstream_http_postbody)
                    ';
            proxy_pass http://localhost:8080;
        }

        location /api-admin {
            internal;
            rewrite_by_lua '
                    ngx.req.set_method(ngx.HTTP_POST)
                    ngx.req.set_body_data(ngx.var.upstream_http_postbody)
                    ';
            proxy_pass http://localhost:8080;
        }

        location /api/search {
            proxy_pass http://localhost:5001;
        }

        location /file/ {
            proxy_pass http://sedna.gobivc.com;
        }

	    location /api/search {
            proxy_pass http://192.168.1.208;
        }
}

less
   npm install less -g
   lessc style.less ../css/style.css


2015.1.1 package中少history
npm install history