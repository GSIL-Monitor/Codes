function config(t,e,l,s){l.when("","/index"),l.otherwise("/index/home"),s.config({debug:!1}),t.interceptors.push(function(){return{request:function(t){return t},response:function(t){var e=t.data;return angular.isString(e)&&"login"==e&&(window.location.href="/login.html"),t}}}),e.state("index",{"abstract":!0,url:"/index",templateUrl:"views/common/content.html"}).state("company",{"abstract":!0,url:"/company",templateUrl:"views/company/company.html"}).state("list",{"abstract":!0,url:"/list",templateUrl:"views/list/list.html"}).state("follow",{"abstract":!0,url:"/follow",templateUrl:"views/follow/list.html"}).state("index.home",{url:"/home",templateUrl:"views/home.html",resolve:{loadPlugin:function(t){return t.load([{serie:!0,name:"angular-flot",files:["js/plugins/flot/jquery.flot.js","js/plugins/flot/jquery.flot.time.js","js/plugins/flot/jquery.flot.tooltip.min.js","js/plugins/flot/jquery.flot.spline.js","js/plugins/flot/jquery.flot.resize.js","js/plugins/flot/jquery.flot.pie.js","js/plugins/flot/curvedLines.js","js/plugins/flot/angular-flot.js"]},{name:"angles",files:["js/plugins/chartJs/angles.js","js/plugins/chartJs/Chart.min.js"]},{name:"angular-peity",files:["js/plugins/peity/jquery.peity.min.js","js/plugins/peity/angular-peity.js"]}])}}}).state("index.search",{url:"/search",templateUrl:"views/search.html"}).state("index.searches",{url:"/searches",templateUrl:"views/save_searches.html"}).state("index.myList",{url:"/my_list",templateUrl:"views/my_list.html"}).state("index.listSearch",{url:"/list_search",templateUrl:"views/list_search.html"}).state("index.news",{url:"/news",templateUrl:"views/news.html"}).state("index.th",{url:"/th",templateUrl:"views/th.html"}).state("company.overview",{url:"/overview",templateUrl:"views/company/overview.html"}).state("company.trends",{url:"/trends",templateUrl:"views/company/trends.html"}).state("company.team",{url:"/team",templateUrl:"views/company/team.html"}).state("company.events",{url:"/events",templateUrl:"views/company/events.html"}).state("list.data",{url:"/data",templateUrl:"views/list/data.html"}).state("list.trends",{url:"/trends",templateUrl:"views/list/trends.html"}).state("list.events",{url:"/events",templateUrl:"views/list/events.html"}).state("follow.data",{url:"/data",templateUrl:"views/follow/data.html"}).state("follow.trends",{url:"/trends",templateUrl:"views/follow/trends.html"}).state("follow.events",{url:"/events",templateUrl:"views/follow/events.html"})}angular.module("gobi").config(config).run(function(t,e){t.$state=e});