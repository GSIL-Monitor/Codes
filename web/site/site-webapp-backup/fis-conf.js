// 设置图片合并的最小间隔
//fis.config.set('settings.spriter.csssprites.margin', 20);

// 取消下面的注释开启simple插件，注意需要先进行插件安装 npm install -g fis-postpackager-simple
 fis.config.set('modules.postpackager', 'simple');

// 取消下面的注释设置打包规则
 fis.config.set('pack', {
     '/pkg/lib.js': [
         'js/functions.js',
         'js/gobi.js'
     ],

     // '/pkg/angular_config.js': [
     //     'js/app.js',
     //     'js/config.js',
     //     'js/controllers.js',
     //     'js/directives.js',
     //     'js/services.js',
     //     'js/translations.js'
     // ],

     '/pkg/jquerys.js': [
     	 'js/jquery/jquery-2.1.1.min.js',
         'js/plugins/metisMenu/jquery.metisMenu.js',
         'js/plugins/slimscroll/jquery.slimscroll.min.js',
         'js/plugins/pace/pace.min.js',
         'js/bootstrap/bootstrap.min.js',
         'js/plugins/jasny/jasny-bootstrap.min.js'
     ],

     '/pkg/angulars.js': [
         'js/angular/angular.min.js',
         'js/angular/angular-touch.min.js',
         'js/angular/angular-cookies.min.js',
         'js/plugins/oclazyload/dist/ocLazyLoad.min.js',
         'js/angular-translate/angular-translate.min.js',
         'js/ui-router/angular-ui-router.min.js',
         'js/bootstrap/ui-bootstrap-tpls-0.12.0.min.js',
         'js/ui-switch/bootstrap-switch.min.js',
         'js/ui-switch/angular-bootstrap-switch.min.js',
         'js/ui-grid/ui-grid.min.js'
     ],

     // 取消下面的注释设置CSS打包规则，CSS打包的同时会进行图片合并
     '/pkg/aio.css': [
         'font-awesome/css/font-awesome.css',
         'css/bootstrap.min.css',
         'css/plugins/ui-switch/bootstrap-switch.min.css',
         'css/plugins/ui-grid/ui-grid.min.css',
         'css/plugins/datepicker/bootstrap-datepicker3.min.css',
         'css/plugins/select2/select2.min.css'
     ]
 });


// 取消下面的注释可以开启simple对零散资源的自动合并
// fis.config.set('settings.postpackager.simple.autoCombine', true);