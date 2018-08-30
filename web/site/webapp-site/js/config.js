/**
 *
 */
function config($httpProvider, $stateProvider, $urlRouterProvider, $ocLazyLoadProvider) {
	$urlRouterProvider.when('', '/index/home');

	//$urlRouterProvider.otherwise("/index/home");

    $ocLazyLoadProvider.config({
        // Set to true if you want to see what and when is dynamically loaded
        debug: false
    });
    
    
    $httpProvider.interceptors.push(function() {
        return {
            'request': function(config){
            	
            	
            	return config; 
            	},
            'response': function(response) {
            
            	var data = response.data;
            	
            	if(angular.isString(data))
            		if(data== 'login')
            			window.location.href="/login.html";
            	
            	return response;
            }
        };
    });
    
    
    
    $stateProvider
        .state('index', {
            abstract: true,
            url: "/index",
            templateUrl: "views/common/content.html"
        })
        .state('company', {
            abstract: true,
            data: { pageTitle: 'Company' },
            url: "/company/:companyCode",
            templateUrl: "views/company/company.html",
            controller: CompanyHeadCtrl
        })
        .state('list', {
            abstract: true,
            data: { pageTitle: 'List' },
            url: "/list",
            templateUrl: "views/list/list.html"
        })
        .state('follow', {
            abstract: true,
            data: { pageTitle: 'Follow' },
            url: "/follow",
            templateUrl: "views/follow/list.html"
        })
        .state('comps', {
            abstract: true,
            data: { pageTitle: 'Comps' },
            url: "/comps",
            templateUrl: "views/comps/comps.html"
        })
        .state('crowdfunding', {
            abstract: true,
            data: { pageTitle: 'Crowdfunding' },
            url: "/crowdfunding/:id",
            templateUrl: "views/crowdfunding/crowdfunding.html",
            controller: CrowdfundingHeadCtrl
        })

        .state('index.home', {
            url: "/home",
            data: { pageTitle: 'Home' },
            templateUrl: "views/home.html"
        })
        .state('index.search', {
            url: "/search",
            data: { pageTitle: 'Search' },
            templateUrl: "views/search.html"
        })
        .state('index.searches', {
            url: "/searches",
            data: { pageTitle: 'Save Searches' },
            templateUrl: "views/save_searches.html"
        })
        .state('index.myList', {
            url: "/my_list",
            data: { pageTitle: 'My Lists' },
            templateUrl: "views/my_list.html"
        })
        .state('index.listSearch', {
            url: "/list_search",
            templateUrl: "views/list_search.html"
        })
        .state('index.news', {
            url: "/news/:companyCode/:newsId",
            data: { pageTitle: 'News' },
            templateUrl: "views/news.html"
        })
        .state('index.crowdfunding', {
            url: "/crowdfunding/:cfStatus/:cfSource",
            data: { pageTitle: 'CrowdFunding' },
            templateUrl: "views/crowdfunding.html"
        })
        
        .state('index.th', {
            url: "/th",
            templateUrl: "views/th.html"
        })
        
        //company
        .state('company.overview', {
            url: "/overview",
            templateUrl: "views/company/overview.html",
            resolve: {
                loadPlugin: function ($ocLazyLoad) {
                    return $ocLazyLoad.load([
                        'release/js/datepicker/bootstrap-datepicker.min.js',
                        'release/js/select2/select2.min.js'
                    ]);
                }
            }
        })
        .state('company.trends', {
            url: "/trends",
            templateUrl: "views/company/trends.html",
            resolve: {
                loadPlugin: function ($ocLazyLoad) {
                    return $ocLazyLoad.load('release/js/highchartJs/highcharts.js');
                }
            }
        })
        .state('company.team', {
            url: "/team",
            templateUrl: "views/company/team.html"
        })
        .state('company.events', {
            url: "/events",
            templateUrl: "views/company/events.html"
        })
        //list
        .state('list.data', {
            url: "/:id/data",
            templateUrl: "views/list/data.html"
        })
        .state('list.trends', {
            url: "/:id/trends",
            templateUrl: "views/list/trends.html"
        })
        .state('list.events', {
            url: "/:id/events",
            templateUrl: "views/list/events.html"
        })
        
        //follow
        .state('follow.data', {
            url: "/data",
            templateUrl: "views/follow/data.html"
        })
        .state('follow.trends', {
            url: "/trends",
            templateUrl: "views/follow/trends.html"
        })
        .state('follow.events', {
            url: "/events",
            templateUrl: "views/follow/events.html"
        })
        
        //comps
        .state('comps.data', {
            url: "/:companyCode/data",
            templateUrl: "views/comps/data.html"
        })

        //crowdfunding
        .state('crowdfunding.data', {
            url: "/data",
            templateUrl: "views/crowdfunding/data.html"
        })
        .state('crowdfunding.view',{
            url:"/view",
            templateUrl: "views/crowdfunding/overview.html"
        })
        .state('crowdfunding.member',{
            url:"/member",
            templateUrl: "views/crowdfunding/member.html"
        })

        
        
}
angular
    .module('gobi')
    .config(config)
    .run(function($rootScope, $state) {
        $rootScope.$state = $state;
    });
