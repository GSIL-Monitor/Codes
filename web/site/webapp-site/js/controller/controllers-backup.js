/**
 * MainCtrl - controller
 */
function MainCtrl($http, $scope, $translate, $cookieStore) {
	
	var ca = document.cookie.split(';');
	var username= '';
	angular.forEach(ca, function(value, key){
		if(value.trim().indexOf('username') == 0){
			username = value.split('=')[1];
		}
	})
	
    this.userName = username;
	
	var lang = $cookieStore.get('ls_language');
	if(lang != null)
		$translate.use(lang);
	
    var mini = $cookieStore.get('ls_mini');
    if(mini != null)
    	$("body").addClass("mini-navbar");
    
   // $cookieStore.put('ls_founded_after', '01/01/2008');
    
    
    $scope.logout = function(){
    	
//    	document.cookie =  'username=; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
//    	document.cookie =  'auto_login=; expires=Thu, 01 Jan 1970 00:00:01 GMT;';

    	var cookieArr = document.cookie.split(';');
    	var username= '';
    	angular.forEach(cookieArr, function(value, key){
    		var cookie = value.split('=');
    		document.cookie =  cookie[0]+'=; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    	})
    	
    	
    	$http.get('./api/user/logout')
	        .success(function(data) {
	        	window.location.href="/login.html";
	        });
    	
    }
    
};



/**
 * translateCtrl - Controller for translate
 */
function TranslateCtrl($translate, $scope, $cookieStore, $window, $location) {
    $scope.changeLanguage = function (langKey) {
        $translate.use(langKey);
        $cookieStore.put('ls_language', langKey);
        
        //if(	($location.absUrl().indexOf('/search')  > 0 ||
    		//$location.absUrl().indexOf('/follow/data') > 0 ||
    		//$location.absUrl().indexOf('/list/data') > 0) &&
    		//$location.absUrl().indexOf('/searches')  < 0 ){
        //
        //}

		$window.location.reload();

//        var lang = langKey;
//        langService.newData(lang);
    };
}


function HomeCtrl($scope, $http, $filter, $window, $location){
	var date = new Date();
	$scope.year = date.getFullYear();
	//$http.get('/api/news/latest?page=1').success(function(data){
	//	var newsList = data.result;
	//
	//	newsList.sort(function(a, b) {
	//			var result =  new Date(b.news.createTime) - new Date(a.news.createTime)
	//			return result
	//		});
	//
	//	$scope.newsList = newsList;
	//
	//})

	$http.get('/api/news/tech?page=1').success(function(data){
		var newsList = data.result;

		newsList.sort(function(a, b) {
			var result =  new Date(b.news.newsDate) - new Date(a.news.newsDate)
			return result
		});

		$scope.techNewsList = newsList;

	})

	$http.get('/api/news/tech/count').success(function(data){
		$scope.total = data.count;
	})


	$scope.href=function(name){

		var active_li;
		if(name.indexOf('search') > -1 && name.indexOf('searches') == -1){
			active_li = $('#li-search');
		}
		else if(name.indexOf('searches') > -1){
			active_li = $('#li-searches');
		}
		else if(name.indexOf('follow') > -1){
			active_li = $('#li-follow');
		}
		else if(name.indexOf('list') > -1){
			active_li = $('#li-list');
		}
		else if(name.indexOf('crowdfunding') > -1){
			active_li = $('#li-crowdfunding');
		}

		if(active_li != null){
			active_li.addClass('active')
				.siblings().removeClass('active');
		}

		$window.location.href = '#/'+name;
	};



	$scope.newsDetail = function(newsId, code){
		$window.location.href= '#/index/news/'+code+'/'+newsId;
	}


	$scope.techDetail = function(newsId){
		$window.location.href= '#/index/news/tech/'+newsId;
	}
}


function SearchCtrl($rootScope, $scope, $http, $cookieStore) {

    $scope.saveSearch = function(){
    	var params = $cookieStore.get('ls_params');
    	
    	var filter = angular.fromJson(params);
    	filter.page = 1;

		$('#save-search').addClass('disabled');


    	if(	filter.names ==null
			&& filter.keywords == null
			&& filter.locations ==null
			&& filter.stages ==null
			&& filter.foundedAfter == null
			&& filter.foundedBefore == null)
		{
    		$('.operate-hint-danger').fadeIn(500).delay(2000).fadeOut(500, function(){
				$('#save-search').removeClass('disabled');
			});
    		return;
    	}
    	

    	
    	var req = {
    			 method: 'PUT',
    			 url: './api/user/search/create',
    			 params: { params: params}
    			}
	    $http(req)
	        .success(function(data) {
	        	$('.operate-hint')
	        		.fadeIn(500)
	        		.delay(2000)
	        		.fadeOut(500, function(){
		        		$('#save-search').removeClass('disabled');
		        	});
	        	
	        })
	        .error(function(error) {
		    })
    }
    
    
    $scope.export = function(){

		exportExcel($rootScope, $scope, $http, $cookieStore);
		

    }
}


/**
 * ModalCtrl
 */

function ModalCtrl($rootScope, $scope, $http, $modal, $log, $cookieStore, gridService) {
	$http.get('./api/common/searchBy').success(function(data){
		$scope.searchItems = data.searchBy;
	    $cookieStore.put('ls_funding_rounds', data.fundingRound);
	})
	
    $scope.open = function (template) {
		openModalFilter($rootScope, $scope, $http, $modal, $cookieStore, gridService, template);
	};
	
	$scope.addMyList = function () {
		
		var arr = angular.fromJson($cookieStore.get('ls_select_rows'));
		var params = []
		angular.forEach(arr, function(value, key){
			params.push(value.companyId);
		})
		
		var req = {
				 method: 'POST',
				 url: './api/company/addMyList',
				 data:  params
				}
		
		$http(req)
		.success(function(data){
			console.log(data)
		})
	};

}

function ModalInstanceCtrl($scope, $modalInstance, $cookieStore) {

	$scope.fundingRounds = $cookieStore.get('ls_funding_rounds');

	$scope.nameItems = $cookieStore.get('name');
	$scope.keywordItems = $cookieStore.get('keyword');
	$scope.locationItems = $cookieStore.get('location');
	$scope.investorItems = $cookieStore.get('investor');
	$scope.stageItems = $cookieStore.get('stage');
	$scope.foundedAfter = $cookieStore.get('founded_after');
	$scope.foundedBefore = $cookieStore.get('founded_before');


    $scope.ok = function () {
        $modalInstance.close();

		//cookieStore change
		cookieComfirm($cookieStore, 'keyword')
		cookieComfirm($cookieStore, 'location');
		cookieComfirm($cookieStore, 'location');
		cookieComfirm($cookieStore, 'investor');
		cookieComfirm($cookieStore, 'name');
		cookieComfirm($cookieStore, 'founded_after');
		cookieComfirm($cookieStore, 'founded_before');

		$cookieStore.put('ls_change', true);
    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.stageInit = function(name){
    	if($scope.stageItems == null) return;
        var result = $scope.stageItems.indexOf(name);
        if(result == -1) 
            this.checked = false;
        else 
            this.checked = true;
    }
    
}



function GridCtrl($rootScope, $scope, $http, $modal, $timeout, $interval, $q, $cookieStore, gridService, $translate, langService) {
	$rootScope.dataCount = 0;
	$scope.mySelections = [];
	
	var fakeI18n = function( title ){
        var deferred = $q.defer();
        $interval( function() {
            deferred.resolve( 'col: ' + title );
        }, 100, 1);
        return deferred.promise;
    };

    var windowHeigh = $( window ).height();
    var rows = 10;
    var num = (windowHeigh-230) / 40;
    	rows = num > rows? num : rows;
    	
    $scope.colDefs = [
                      { field: 'productName', name: $translate.instant('NAME'), width:'16%', minWidth:100,  enableSorting: false, enableHiding: false,
                          cellTemplate: '<div class="grid-name ui-grid-cell-contents">' +
						  //'<img src="file/{{row.entity.logo}}/logo.jpg"  height="30"/>'+
						  '<a href="#/company/{{row.entity.companyCode}}/overview">{{row.entity.productName}}</a>' +
						  '<span class="grid-verify" ng-show="row.entity.verify == '+"'Y'"+'">{{"VERIFIED" | translate}}</span></div>',
                          menuItems: [{
                                      title: $translate.instant('NAME_FILTER'),
                                      icon: 'ui-grid-icon-filter',
                                      action: function(){
                                    	  openModalFilter($rootScope, $scope, $http, $modal, $cookieStore, gridService, 'name');
                                      }
                        	}]
                        },
                        { field: 'keywords' , name: $translate.instant('KEYWORDS'), width:'12%', minWidth:100,  enableSorting: false, enableHiding: false,
                          menuItems: [{
                	            	  title: $translate.instant('KEYWORD_FILTER'),
                	            	  icon: 'ui-grid-icon-filter',
                	            	  action: function(){
                	            		  openModalFilter($rootScope, $scope, $http, $modal, $cookieStore, gridService, 'keyword');
                	            	  }
                	            	}]
                        },
                        { field: 'companyDesc' , name: $translate.instant('DESC'), width:'42%', minWidth:300,  enableSorting: false,
                          cellTemplate: '<div class="grid-desc ui-grid-cell-contents tool" title="{{row.entity.companyDesc}}">'
                        		+'{{row.entity[col.field]}}'
                        		+'</div>'},
                        { field: 'stage', name: $translate.instant('STAGE'), width:'6%', minWidth:60},
                        { field: 'location' , name: $translate.instant('LOC'), width:'6%', minWidth:60, enableHiding: false,
                    	  menuItems: [{
                        	  title: $translate.instant('LOCATION_FILTER'),
                        	  icon: 'ui-grid-icon-filter',
                        	  shown: true
                        	}]},
                    	//{ field: 'status', name: $translate.instant('STATUS'), width: '8%', minWidth:80},
                    	{ field: 'website', name: $translate.instant('WEBSITE') , minWidth:150,  enableSorting: false,
                        	cellTemplate: '<div class="grid-website ui-grid-cell-contents">'+
                        		'<span ng-show="row.entity.website == null || row.entity.website.length == 0">N/A</span>'+
                        		'<a href="{{row.entity[col.field]}}" target="_blank" ng-show="row.entity.website != null">{{row.entity[col.field]}}</a></div>'}
                    ];
	$cookieStore.remove('ls_select_rows');//unknow
    $scope.gridOptions = {
    	headerRowHeight: 50,
    	rowHeight:40,
    	minRowsToShow: rows,
        exporterMenuCsv: false,
        enableGridMenu: true,
        enableRowSelection: true,
        enableSelectAll: true,
        infiniteScrollRowsFromEnd: 20,
        infiniteScrollUp: true,
        infiniteScrollDown: true,
        gridMenuTitleFilter: fakeI18n,
        columnDefs: $scope.colDefs,

        data: 'data',
        onRegisterApi: function(gridApi){
            $scope.gridApi = gridApi;
            gridApi.selection.on.rowSelectionChanged($scope,function(row){

              var list = [];
              angular.forEach(gridApi.selection.getSelectedRows(), function(value, key){
					var code = value.companyCode;
					this.push(code);
				}, list)
				
			  $cookieStore.put('ls_select_rows',list);

              $rootScope.dataCount = gridApi.grid.selection.selectedCount;
            });
            gridApi.selection.on.rowSelectionChangedBatch($scope,function(rows){
              
            	var list = [];
                angular.forEach(gridApi.selection.getSelectedRows(), function(value, key){
  					var code = value.companyCode;
  					this.push(code);
  				}, list)
  				
  			   $cookieStore.put('ls_select_rows',list);

               
            	$rootScope.dataCount = gridApi.grid.selection.selectedCount;
            });
            
            gridApi.infiniteScroll.on.needLoadMoreData($scope, $scope.getDataDown);
            gridApi.infiniteScroll.on.needLoadMoreDataTop($scope, $scope.getDataUp);
            
        }
       
    };
    $scope.data = [];
    $scope.firstPage = 1;
    $scope.lastPage = 1;
    $scope.totalPage = 10;
    
    $cookieStore.put('ls_page', 1);
    $cookieStore.put('ls_change', true);
    change($rootScope, $scope, $http, $cookieStore, gridService);
    
   
      // Scroll Data
     
      $scope.getDataDown = function() {
    	  
    	  if(gridService.getData().length< 50) return;
    	  
    	  $scope.page = $cookieStore.get('ls_page');
    	  if($scope.page == 10 ) return;
	      $cookieStore.put('ls_page', ++$scope.page);
    	  $cookieStore.put('ls_change', true);
		  var params = getParams($rootScope, $scope, $cookieStore);

		  var codeArr = [];
		  var req = {
		     method: 'POST',
		     url: '/api/search/company',
		     headers: {'Content-Type': 'application/json'},
		     data:  params,
		     responseType: 'json'
		    }
	   
	       $http(req)
		        .success(function(data) {
		          $rootScope.total = data.total;
			      codeArr = data.companyIds;
		        })
		        .then(function(){
	    	      if(codeArr.length == 0){
		            return;
		          }
	    	      
	    	      var promise = $q.defer();
		          var reqDetail = {
		               method: 'POST',
		               url: './api/company/getCompanies',
		               params: { codes: codeArr}
		              }
	             $http(reqDetail)
	              .success(function(data) {
	            	  //console.log(idArr)
	            	  $scope.lastPage++;
	            	  var newData = data.companyList;
	    		      $scope.gridApi.infiniteScroll.saveScrollPercentage();
	    	          $scope.data = $scope.data.concat(newData);
	    		      $scope.gridApi.infiniteScroll.dataLoaded($scope.firstPage > 1, $scope.lastPage < $scope.totalPage).then(function() {
	    		    	  promise.resolve();
	    		      });
	              })
	              .error(function(error) {
	                  $scope.gridApi.infiniteScroll.dataLoaded();
	                  promise.reject();
	                });
		        
		      });
       
      };

      $scope.$watch(function(){return gridService.getData()}, function (newValue, oldValue) {
      	  if (newValue === oldValue) return;
      	  
      	  $scope.gridApi.infiniteScroll.resetScroll();
      	  $scope.data = gridService.getData();
      });
      
}


function KeywordSwitchCtrl($scope, $cookieStore) {
  $scope.onText = 'AND';
  $scope.offText = 'OR';
  $scope.isActive = true;
  $scope.size = 'mini';
  $scope.offColor = 'primary';
  $scope.animate = true;
  $scope.radioOff = true;
  
  if($cookieStore.get('ls_keyword_switch')) $scope.isSelected= true;

  $scope.$watch('isSelected', function (newValue, oldValue) {
  	  if (newValue === oldValue) {
        return;
      }
  	  if($scope.isSelected != undefined && $scope.isSelected != null){
  		  $cookieStore.put('ls_keyword_switch',  $scope.isSelected);
  	  }else{
  		$cookieStore.put('ls_keyword_switch',  null);
  	  }
	  $cookieStore.put('ls_change',  true);
  });
}

function InvestorSwitchCtrl($scope, $cookieStore) {
	  $scope.onText = 'AND';
	  $scope.offText = 'OR';
	  $scope.isActive = true;
	  $scope.size = 'mini';
	  $scope.offColor = 'primary';
	  $scope.animate = true;
	  $scope.radioOff = true;

	  if($cookieStore.get('ls_investor_switch')) $scope.isSelected= true;
	  
	  $scope.$watch('isSelected', function(newValue, oldValue) {
	  	  if (newValue === oldValue) {
	          return;
	      }
	  	  
	  	  if($scope.isSelected != undefined && $scope.isSelected != null){
	  		  $cookieStore.put('ls_investor_switch',  $scope.isSelected);
	  	  }else{
	  		$cookieStore.put('ls_investor_switch',  null);
	  	  }
	  	  
		  $cookieStore.put('ls_change',  true);
	  });
	}


/**
 * DataPicker Controller on founded_modal.html
 * @param $scope
 */
function DatepickerCtrl($scope, $cookieStore) {
	  $scope.today = function() {
	    $scope.dt = new Date();
	  };

	  var after = $cookieStore.get('ls_founded_after');
	  var before = $cookieStore.get('ls_founded_before');
	  if(after == null)  {
		  $scope.dt = '01/01/2012';
		  $cookieStore.put('founded_after', $scope.dt);
		  $cookieStore.put('ls_change', true);
	  }
	  else $scope.dt = after;
	 
	  
	  if(before != null )$scope.dt2 = before;

	  $scope.clear = function () {
	    $scope.dt = null;
	  };

	  $scope.open = function($event, order) {
	    $event.preventDefault();
	    $event.stopPropagation();
	    
	    if(order == 1){
	    	$scope.order1opened = true;
	 	    $scope.order2opened = false;
	    }else{
		    $scope.order1opened = false;
		    $scope.order2opened = true;
	    }
	    
	  };

	  $scope.dateOptions = {
	    formatYear: 'yy',
	    startingDay: 1
	  };

	  $scope.formats = ['dd-MMMM-yyyy', 'yyyy/MM/dd', 'dd.MM.yyyy', 'MM/dd/yyyy'];
	  $scope.format = $scope.formats[3];
	  
}



//function CompanyHeadCtrl($rootScope, $scope, $http, $location, $translate, $stateParams){
//	var location = $location.absUrl();
//	var code = $stateParams.companyCode;
//	var name = '';
//	var headInfo = '';
//
//    $http.get('./api/company/head?code='+code).success(function(data){
//    	$scope.headInfo = data.headInfo;
//    	headInfo = data.headInfo;
//    	name = $scope.headInfo.name;
//
//    	setPageTitle(name);
//
//    	var logo = headInfo.logo;
//    	if(logo != null){
//    		angular.element("#company-logo").append("<img src='/file/"+logo+"/logo.jpg'  height='30' style='margin-bottom:8px;'/>");
//    	}
//    	if(headInfo.verify =='Y'){
//    		var span = '<span class="company-verify ">'+$translate.instant('VERIFIED')+'</span>';
//    		angular.element("#company-verify").append(span)
//    	}
//
//    }).error(function(){
//    	$location.path('/');
//
//    }).then(function(){
//
//    	$http.get('/api/news/exist?code='+code).success(function(data){
//    		if(data == 'Y') {
//    			var li_class = '<li id="li-events"class="li-href" >';
//    			if (location.indexOf('events') > -1)
//    				li_class = '<li id="li-events"class="li-href cate-active" >';
//
//    			var li = li_class +
//    				'	<a href="#/company/' + headInfo.companyCode + '/events" category-filter>' +
//    				'		<span class="fa-stack ft15">' +
//    				'		<i class="fa fa-circle-thin fa-stack-2x"></i>' +
//    				'		<i class="fa fa-flag fa-stack-1x"></i>' +
//    				'		</span>' +
//    				$translate.instant('EVENTS') +
//    				'	</a>' +
//    				'</li>';
//    			$("#company-head-ul").append(li);
//    		}
//    	}).then(function(){
//    		$http.get('/api/trends/exist?code='+code).success(function(data){
//    			$scope.trends = data;
//    			if($scope.trends == 'Y'){
//    				var li_class = '<li id="li-trends"class="li-href" >';
//    				if(location.indexOf('trends')>-1)
//    					li_class =  '<li id="li-trends"class="li-href cate-active" >';
//
//    				var li = li_class+
//    					'<a href="#/company/'+headInfo.companyCode+'/trends" category-filter>'+
//    					'	<span class="fa-stack ft15"> '+
//    					'	<i class="fa fa-circle-thin fa-stack-2x"></i>'+
//    					'		<i class="fa fa-bar-chart fa-stack-1x"></i>'+
//    					'		</span> '+
//    					$translate.instant('TRENDS')+
//    					'	</a> '+
//    					'	</li>';
//    				$("#company-head-ul").append(li);
//    			}
//    		})
//    	})
//    })
//
//
//
//
//
//    $scope.verify = function(){
//		var req = {
//			method: 'put',
//			url: './api/company/verify',
//			params: { code: code, verify: 'Y'}
//		}
//		$http(req).success(function(data){
//
//		}).then(function(){
//			alertDiv($translate.instant('SAVED'), $translate.instant('COMPANY_VERIFIED_SUCCESS'));
//		})
//    }
//
//
//
//    $scope.$watch(function(){return $location.absUrl()}, function (newValue, oldValue) {
//	   	  if (newValue === oldValue) return;
//	   	  if(newValue.indexOf('overview') > -1){
//	   		$('#li-overview').addClass('cate-active')
//	   				.siblings().removeClass('cate-active');
//	   	  }
//		  else if(newValue.indexOf('team') > -1){
//			  $('#li-team').addClass('cate-active')
//				  .siblings().removeClass('cate-active');
//		  }
//	   	  else if(newValue.indexOf('trends') > -1){
//	   		$('#li-trends').addClass('cate-active')
//	   				.siblings().removeClass('cate-active');
//	   	  }
//		  else if(newValue.indexOf('crowdfunding') > -1){
//			  $('#li-cf').addClass('cate-active')
//				  .siblings().removeClass('cate-active');
//		  }
//	   	  else if(newValue.indexOf('events') > -1){
//	   		 $('#li-events').addClass('cate-active')
//	   		 		.siblings().removeClass('cate-active');
//	   	  }
//
//		  //setPageTitle(name)
//    });
//
//}




function CompanyTeamCtrl($scope, $http, $location, $stateParams){

	var code = $stateParams.companyCode;

	var date = new Date();
	$scope.year = date.getFullYear();

	$http.get('./api/company/team?code='+code).success(function(data){
		$scope.team = data.team;
		$scope.jobs = data.jobs;
		$scope.recruit = data.recruit;

		//if(jobs != null){
		//	jobs = $.parseJSON(jobs.jobs)
        //
		//	jobs.sort(function(a, b) {
		//		var result =  date2Timestap(b.bornTime.slice(0,10)) - date2Timestap(a.bornTime.slice(0,10));
		//		return result
		//	});
        //
		//	$scope.jobs = jobs;
		//}


	}).error(function(){
		$location.path('/');
	})
}


function CompanyEventsCtrl($scope, $http, $location, $window, $stateParams){

	var code = $stateParams.companyCode;

	var date = new Date();
	$scope.year = date.getFullYear();

	$http.get('/api/news/getByCompany?code='+code+'&page=1').success(function(data){
		$scope.newsList = data.result;
		console.log(data)
	}).error(function(){
		$location.path('/');
	})

	$scope.newsDetail = function(nId){
		$window.location.href= '#/index/news/'+code+'/'+nId;
	}

}


function BasicModalCtrl($scope, $http, $modal, $cookieStore, $location, $translate, listService, $stateParams) {
	
	 $scope.open = function (template) {
		 
		 if(template == 'profile'){
			 $http.get('./api/user/profile').success(function(data){
					$scope.profile = data.profile;
					$cookieStore.put('ls_profile', $scope.profile);
				})
		 }
		 
		 if(template == 'list'){
			var code =  $stateParams.companyCode
			 if (code != null){
				 var select = [];
				select.push(code);
				$cookieStore.put('ls_select_rows', select);
			 }

			 // company overview
			 var companyCodes = $cookieStore.get('ls_select_rows');
			 if(companyCodes == null){
				 companyCodes =  $cookieStore.get('ls_company');
				 $cookieStore.put('ls_select_rows', companyCodes);
			 }
			 
			 $cookieStore.remove('ls_add_list');
		 }
		 
		 var modalInstance = $modal.open({
		        templateUrl: "./views/modal/user/"+template+"_modal.html",
		        controller: 'BasicModalInstanceCtrl',
		        resolve: {
	                template: function(){
	                	return template;
	                }
		 
	            }
		    });

	    modalInstance.result.then(function (callBack) {
	    	
	    	// create list
	    	if(template == 'create_list'){
	    		if(callBack.listName == null || callBack.listName== '') return;
	    		
	    		var req = {
	   				 method: 'put',
	   				 url: './api/user/list/create',
	   				 params: { name: callBack.listName}
	   		    }
	   		
		   		$http(req).success(function(data){
		   		}).then(function(){
		   			
		   			$http.get('./api/user/list/get?page=1').success(function(data){
		   				$scope.page = 1;
		   				$scope.userList = data.userList;
		   				$scope.total = data.total;
		   				listService.newData(data.userList);
					})
					
					alertDiv($translate.instant('SAVED'), $translate.instant('CREATE_NEW_LIST_SUCCESS'));
					
		   		})
		   		
	    	}
	    	
	    	
	    	if(template == 'list'){
	    		
	    		// add companies to list
	        	var req = {
		   				 method: 'put',
		   				 url: './api/company/list/add',
		   				 params: { listIds: callBack.list,
							       companyCodes: callBack.companyCodes}
		   		    }
		   		
			   		$http(req).success(function(data){
			   		}).then(function(){
			   			alertDiv($translate.instant('SAVED'), $translate.instant('ADD_TO_SELECTED_LIST'));
			   		})
	    	}
	    	
	    	
	    });
	};
	
}

function BasicModalInstanceCtrl( $scope, $modalInstance, $cookieStore, template) {
	
	$scope.callBack = {};
	
	if(template == 'profile')
		$scope.profile = $cookieStore.get('ls_profile');
	
    $scope.ok = function () {
    	if(template == 'create_list')
    		$scope.callBack.listName = $('#list-name').val();
    	
    	if(template =='comfirm')
    		$scope.callBack.comfirm = true;
    		
    	$modalInstance.close($scope.callBack);
    };

    //company add to list
    $scope.addConfirm = function(){
    	var list = $cookieStore.get('ls_add_list');
    	
    	if(list == null || list.length == 0){
    		$('.select-list').css('display', 'block');
    		return;
    	}
    	
    	$scope.callBack.list = list;
    	$scope.callBack.companyCodes = $cookieStore.get('ls_select_rows');
    	

    	$modalInstance.close($scope.callBack);
    }
    
    
    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };
}




function EditModalCtrl($rootScope, $scope, $http, $modal, $cookieStore, $translate){

	 $scope.open = function (template, info) {
		 var modalInstance = $modal.open({
		        templateUrl: "./views/modal/user/"+template+"_modal.html",
		        controller: 'EditModalInstanceCtrl',
		        resolve: {
	                template: function(){
	                	return template;
	                },
	                info: function(){
	                	return info;
	                }
	            }
		    });
		 
		 
		 modalInstance.result.then(function (callBack) {
		    	
		    	// edit List
		    	if(template == 'edit_list'){
		    		if(callBack.listName == null || callBack.listName== '') return;
		    		
		    		
		    		$http.get('./api/user/list/getById?id='+callBack.listId)
		    			.success(function(data){
		    				
		    				if( data.list.listName == callBack.listName &&
		    					data.list.listDesc == callBack.listDesc &&
		    					data.list.listStatus == callBack.listStatus)
		    					return;
		    				
		    				var req = {
		   		   				 method: 'put',
		   		   				 url: './api/user/list/update',
		   		   				 params: { name: callBack.listName,
		   		   					 	   desc: callBack.listDesc,
		   		   					 	   listStatus: callBack.listStatus,
		   		   					 	   id: callBack.listId}
		   		   		    }
		   		   		
		   			   		$http(req).success(function(data){
		   			   		}).then(function(){
		   			   			
		   			   			$http.get('./api/user/list/get?start=0').success(function(data){
		   				   			$rootScope.userList = data.userList;
		   						}).then(function(){
		   							alertDiv($translate.instant('SAVED'), $translate.instant('UPDATE_LIST_SUCCESS'));
		   						})
		   			   		})
		    				
		    			})
			   		
		    	}
		    	
		    });
	 }
}


function EditModalInstanceCtrl($scope, $http, $modalInstance, $cookieStore, template, info) {
	
	$scope.callBack = {};
	
	if(template == 'edit_list'){
		var list = angular.fromJson(info);
		var req = {
  				 method: 'get',
  				 url: './api/user/list/getById',
  				 params: {id: list.listId}
  		    }
  		
	   		$http(req).success(function(data){
	   			$scope.editList = data.list;
	   		})
	   	
	}
		
	
    $scope.ok = function () {

    	if(template == 'edit_list'){
    		$scope.callBack.listName = $('input[name=listName]').val();
    		$scope.callBack.listDesc = $('input[name=listDesc]').val();
    		$scope.callBack.listStatus = $('input[name=listStatus]:checked').val();
    		$scope.callBack.listId = $scope.editList.listId;
    	}
    	
    	$modalInstance.close($scope.callBack);
    		
    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };
}



function SaveSearchCtrl( $scope, $http, $filter, $cookieStore) {
	$scope.page = 1;
	
	$http.get('./api/user/search/get?page=1').success(function(data){
		$scope.total = data.total;
		var list = [];
		angular.forEach(data.searchList, function(value, key){
			var ele = {};
			ele = value;
			parseSearchParams($filter, ele);
			
			this.push(ele);
		}, list)
		
		$scope.searchList = list;
	})
	
}



function ListCtrl($scope, $http, listService) {
	$scope.page = 1;
	
	$http.get('./api/user/list/get?page=1').success(function(data){
		$scope.userList = data.userList;
		$scope.heartList = data.heartList;
		$scope.total = data.total;
		listService.newData(data.userList);
	})
	
	$scope.$watch(function(){return listService.getData()}, function (newValue, oldValue) {
   	  if (newValue === oldValue) return;
   	  $scope.userList = newValue;
   });
	 
}

function ListDetailCtrl($rootScope, $scope, $http, $modal, $location, $cookieStore, listGridService, $translate, $stateParams){
	
	var id = $stateParams.id;
	
	$http.get('./api/user/list/overview?id='+id).success(function(data){
		$scope.listInfo = data.listInfo;
		$scope.companyList = data.companyList;
		$rootScope.total = data.companyList.length;
		listGridService.newData($scope.companyList);

		setPageTitle($scope.listInfo.listName)

	}).error(function(){
		$location.path('/index/my_list');
	})
	
	$scope.share = function(){
		var status = $scope.listInfo.listStatus;
		var req = {
				 method: 'put',
				 url: './api/user/list/updateStatus',
				 params: { id: id, status: status}
		    }
		
		$http(req).success(function(data){
			
		}).then(function(){
			if(status == 1001){
				$scope.listInfo.listStatus = 1002;
				alertDiv($translate.instant('SAVED'), $translate.instant('SHARE_SUCCESS'));
			}
				
			else{
				$scope.listInfo.listStatus = 1001;
				alertDiv($translate.instant('SAVED'), $translate.instant('CLOSE_SHARE_SUCCESS'));
			}
				
		})
	}

	$scope.deleteSelected = function(){
		var modalInstance = comfirm($modal);
		 modalInstance.result.then(function (callBack) {
			 if(callBack.comfirm){
				var codes = $cookieStore.get('ls_select_rows');
				var req = {
						method: 'delete',
						url: './api/company/list/delete',
						params: {listId: $scope.listInfo.listId,
								companyCodes : codes}
					}
				
				$http(req).success(function(data){
					 $http.get('./api/user/list/overview?id='+id).success(function(data){
							$scope.listInfo = data.listInfo;
							$scope.companyList = data.companyList;
							$rootScope.total = data.companyList.length;
							listGridService.newData($scope.companyList);
							$rootScope.listSelectedCount = 0;
					 })
				}).then(function(){
					$cookieStore.remove('ls_select_rows');
					alertDeleteDiv($translate.instant('DELETED'), $translate.instant('DELETE_FROM_LIST'))
				})
			 }
		 });
	}
	
}

function ListModalCtrl($scope, $http, $cookieStore, $location) {
	
	getAllList( $scope, $http, $cookieStore, $location);
	
	
	$scope.createButton = function(){
		$('#hide-create-list').show();
		$('#div-create-list').show();
		$('#a-create-list').hide();
	}
	
	$scope.hideButton = function(){
		$('#hide-create-list').hide();
		$('#div-create-list').hide();
		$('#a-create-list').show();
	}
	
}






function ListGridCtrl($rootScope, $scope, $interval, $q, $cookieStore, $translate, listGridService) {

    $scope.colDefs = [
						{ field: 'company', name: $translate.instant('NAME'), width:'16%', minWidth:100,  enableSorting: false, enableHiding: false,
							cellTemplate: '<div class="grid-name ui-grid-cell-contents"><a href="#/company/{{row.entity.company.companyCode}}/overview">{{row.entity.company.name}}</a>' +
							'<span class="grid-verify" ng-show="row.entity.verify == '+"'Y'"+'">{{"VERIFIED" | translate}}</span></div>',
							menuItems: [{
								title: $translate.instant('NAME_FILTER'),
								icon: 'ui-grid-icon-filter',
								action: function(){
									openModalFilter($rootScope, $scope, $http, $modal, $cookieStore, gridService, 'name');
								}
							}]
						},
						{ field: 'keywords' , name: $translate.instant('KEYWORDS'), width:'12%', minWidth:100,  enableSorting: false, enableHiding: false,
							menuItems: [{
								title: $translate.instant('KEYWORD_FILTER'),
								icon: 'ui-grid-icon-filter',
								action: function(){
									openModalFilter($rootScope, $scope, $http, $modal, $cookieStore, gridService, 'keyword');
								}
							}]
						},
						{ field: 'companyDesc' , name: $translate.instant('DESC'), width:'30%', minWidth:300,  enableSorting: false,
							cellTemplate: '<div class="grid-desc ui-grid-cell-contents tool" title="{{row.entity.companyDesc}}">'
							+'{{row.entity[col.field]}}'
							+'</div>'},
                        { field: 'establishDate' , name: $translate.instant('FOUNDED'), width:'6%', minWidth:60,
                		  cellTemplate:'<div class="grid-name ui-grid-cell-contents">'+
                						 '<span ng-hide="row.entity.establishDate != null">N/A</span>'+
                						 '<span ng-show="row.entity.establishDate != null">{{row.entity.establishDate.slice(0,7)}}</span>'+
                						 '</div>'
                        },
                        { field: 'stage', name: $translate.instant('STAGE'), width:'6%', minWidth:60},
                        { field: 'location' , name: $translate.instant('LOC'), width:'6%', minWidth:60, enableHiding: false},
                        { field: 'status', name: $translate.instant('STATUS'), width: '6%', minWidth:60},
                        { field: 'website', name: $translate.instant('WEBSITE') , minWidth:150,  enableSorting: false,
                        	cellTemplate: '<div class="grid-website ui-grid-cell-contents">'+
                        	    '<span ng-show="row.entity.website == null || row.entity.website.length == 0">N/A</span>'+
                        		'<a href="{{row.entity[col.field]}}" target="_blank" ng-show="row.entity.website != null">{{row.entity[col.field]}}</a></div>'}
                    ];


	$cookieStore.remove('ls_select_rows')
	gridBasic($rootScope, $scope, $interval, $q, $cookieStore, 'ls_select_rows', listGridService)
	 
}

//function FollowGridCtrl($rootScope, $scope, $interval, $q, $cookieStore, $translate, listGridService) {
//
//
//	$scope.colDefs = [
//		{ field: 'productName', name: $translate.instant('NAME'), width:'16%', minWidth:100,  enableSorting: false, enableHiding: false,
//			cellTemplate: '<div class="grid-name ui-grid-cell-contents"><a href="#/company/{{row.entity.companyCode}}/overview">{{row.entity.productName}}</a>' +
//			'<span class="grid-verify" ng-show="row.entity.verify == '+"'Y'"+'">{{"VERIFIED" | translate}}</span></div>',
//			menuItems: [{
//				title: $translate.instant('NAME_FILTER'),
//				icon: 'ui-grid-icon-filter',
//				action: function(){
//					openModalFilter($rootScope, $scope, $http, $modal, $cookieStore, gridService, 'name');
//				}
//			}]
//		},
//		{ field: 'keywords' , name: $translate.instant('KEYWORDS'), width:'12%', minWidth:100,  enableSorting: false, enableHiding: false,
//			menuItems: [{
//				title: $translate.instant('KEYWORD_FILTER'),
//				icon: 'ui-grid-icon-filter',
//				action: function(){
//					openModalFilter($rootScope, $scope, $http, $modal, $cookieStore, gridService, 'keyword');
//				}
//			}]
//		},
//		{ field: 'companyDesc' , name: $translate.instant('DESC'), width:'30%', minWidth:300,  enableSorting: false,
//			cellTemplate: '<div class="grid-desc ui-grid-cell-contents tool" title="{{row.entity.companyDesc}}">'
//			+'{{row.entity[col.field]}}'
//			+'</div>'},
//		{ field: 'establishDate' , name: $translate.instant('FOUNDED'), width:'6%', minWidth:60,
//			cellTemplate:'<div class="grid-name ui-grid-cell-contents">'+
//			'<span ng-hide="row.entity.establishDate != null">N/A</span>'+
//			'<span ng-show="row.entity.establishDate != null">{{row.entity.establishDate.slice(0,7)}} </span>'+
//			'</div>'
//		},
//		{ field: 'stage', name: $translate.instant('STAGE'), width:'6%', minWidth:60},
//		{ field: 'location' , name: $translate.instant('LOC'), width:'6%', minWidth:60, enableHiding: false},
//		{ field: 'fStatus', name: $translate.instant('FOLLOWSTATUS'), width: '10%', minWidth:100},
//		{ field: 'followStart', name: $translate.instant('FOLLOWSTART') , minWidth:100,
//			cellTemplate: '<div class="ui-grid-cell-contents">'+
//			'<span ng-hide="row.entity.followStart != null">N/A</span>'+
//			'<span ng-show="row.entity.followStart != null">{{row.entity.followStart.slice(0,10)}}'+
//			'</div>'
//		}
//	];
//
//	$cookieStore.remove('ls_select_rows')
//	gridBasic($rootScope, $scope, $interval, $q, $cookieStore, 'ls_select_rows', listGridService)
//
//}



function NewsCtrl($scope, $http, $location, $stateParams){

	var code = $stateParams.companyCode;
	$scope.companyCode = code;
	var newsId = $stateParams.newsId;
	
	$http.get('/api/news/detail?code='+code+'&newsId='+newsId).success(function(data){
		$scope.news = data.result;

		setPageTitle($scope.news.news.newsTitle)

		var contentList = data.result.contents;
		angular.forEach(contentList, function(value, key){

			if(value.content == null || value.content ==""){
				if(value.imgae != null || value.image != ""){
					var img = value.image;
					if(img.indexOf('jpg')==-1 && img.indexOf('png')==-1 && img.indexOf('jpeg')==-1)
						img = "/file/"+img+"/news.jpg";
					value.image = img;
					$("#content").append("<p style='text-align: center'><img src='"+img+"'/></p>")
				}
			}else{
				$("#content").append("<p>"+value.content+"</p>")
			}
		})

	}).error(function(){
		$location.path('/');
	}).then(function(){
		if (code =='tech')
			return

		$http.get('./api/company/name?code='+code).success(function(data){
			$scope.name = data.name;
			$scope.code = code;
		})

	})
}


function ThCtrl($scope, $http, $cookieStore, $window, $translate){
	
	$cookieStore.remove('th_special');
	$cookieStore.remove('th_using');
	$cookieStore.remove('th_wastes');
	
	$scope.currentPage = $cookieStore.get('currentPage');
	if($scope.currentPage == null) $scope.currentPage =1;
	
	$scope.maxSize = 10;
	$scope.bigTotalItems = 1000;
	
	$http.get('./api/thesaurus/get?page='+ $scope.currentPage).success(function(data){
		$scope.list = data.list;
		$scope.total = data.total;
	})
	var special = $cookieStore.get('th_special');
	var using = $cookieStore.get('th_using');
	var waste = $cookieStore.get('th_waste');
	
	
	$scope.setPage = function (pageNo) {
	  $scope.currentPage = pageNo;
	};

	$scope.pageChanged = function() {
		$cookieStore.put('currentPage', $scope.currentPage);
		$window.location.reload();
	};
	
	$scope.update = function(){
		var specials = $cookieStore.get('th_special');
		console.log(specials)
		if(specials != null && specials != undefined && specials.length >0){
			var req = {
	   			 method: 'PUT',
	   			 url: './api/thesaurus/update',
	   			 params: { ids: specials, type: 1101}
	   			}
		    $http(req).success(function(data) {
				$window.location.href = '#/index/th';
				$cookieStore.remove('th_special');
				alertDiv($translate.instant('SAVED'), $translate.instant('Specail..'));
	        })
		}
		
		var usings = $cookieStore.get('th_using');
		console.log(usings)
		if(usings != null && usings != undefined && usings.length >0){
			var req = {
	   			 method: 'PUT',
	   			 url: './api/thesaurus/update',
	   			 params: { ids: usings, type: 1102}
	   			}
		    $http(req).success(function(data) {
				$window.location.href = '#/index/th';
				$cookieStore.remove('th_using');
		    	alertDiv($translate.instant('SAVED'), $translate.instant('Using..'));
	        })
		}
		
		var wastes = $cookieStore.get('th_waste');
		console.log(wastes)
		if(wastes != null && wastes != undefined && wastes.length >0){
			var req = {
	   			 method: 'PUT',
	   			 url: './api/thesaurus/update',
	   			 params: { ids: wastes, type: 1103}
	   			}
		    $http(req).success(function(data) {
				$window.location.href = '#/index/th';
				$cookieStore.remove('th_waste');
		    	alertDiv($translate.instant('SAVED'), $translate.instant('Waste..'));
	        })
		}
	}

}


function CompsCtrl($scope, $http, $location, $modal, $cookieStore, $rootScope, $translate, compsGridService, $stateParams) {

	var code = $stateParams.companyCode;
	$(document.body).animate({'scrollTop':0},100);

	companyCodes = [];

	$scope.labels = ['PRODUCT', 'FULL_NAME', 'FOUNDED', 'LOCATION', 'FUNDING', 'TEAM', 'OPERATING_DATA']


	$http.get('./api/company/overview?code='+code).success(function(data) {
		$scope.company = data.company;
		$scope.relates = data.company.relCompanies;

		companyCodes.push($scope.company.companyCode)

		angular.forEach($scope.relates, function(value, key){
			var id = value.companyCode;
			this.push(id);
		}, companyCodes)

		//var codes = $cookieStore.get('ls_comps_select');
        //
		//if (codes != null){
		//	for (var i = companyCodes.length; i--;) {
		//		for (var d= codes.length; d--;){
		//			if (companyCodes[i] == codes[d] )
		//				companyCodes.splice(i, 1);
		//		}
		//	}
		//}

	}).then(function(){
		var req = {	method: 'POST',
					url: './api/comps/get',
					params: { codes: companyCodes}
		           }
		$http(req).success(function(data) {
			$scope.comps = data.comps;
			compsGridService.newData($scope.comps);
		})
	})



	$scope.deleteSelected = function(){
		var modalInstance = comfirm($modal);
		modalInstance.result.then(function (callBack) {
			if(callBack.comfirm){

				// splice
				var codes = $cookieStore.get('ls_comps_select');

				if (codes != null){
					for (var i = companyCodes.length; i--;) {
						for (var d= codes.length; d--;){
							if (companyCodes[i] == codes[d] )
								companyCodes.splice(i, 1);
						}
					}
				}

				var req = {	method: 'POST',
					url: './api/comps/get',
					params: { codes: companyCodes}
				}

				$http(req).success(function(data){
					$scope.comps = data.comps;
					compsGridService.newData($scope.comps);
					$rootScope.listSelectedCount = 0;

				}).then(function(){
					alertDeleteDiv($translate.instant('DELETED'), $translate.instant('DELETE_FROM_LIST'))
				})
			}
		});

	}


	$scope.addComps = function(){
		var name = $('#add-company').val()
		$http.get('./api/company/getByName?name='+name).success(function(data){
			var code = data.code;
			if(code == null || code == '') return;

			var exist = false;
			for (var i = companyCodes.length; i--;) {
				if (companyCodes[i] == code )
					exist = true;
			}
			if(exist) return;


			var codes = []
			codes.push(code);
			companyCodes.push(code);

			var req = {	method: 'POST',
				url: './api/comps/get',
				params: { codes: codes}
			}

			$http(req).success(function(data) {

				$scope.comps.push(data.comps[0]);
				console.log($scope.comps)
				compsGridService.newData($scope.comps);
			}).then(function(){
				alertDeleteDiv($translate.instant('ADDED'), $translate.instant('ADDED_INTO_COMPS'))
			})

		})
	}
}



function CompsGridCtrl($rootScope, $scope, $http, $modal, $timeout, $interval, $q, $cookieStore, compsGridService, $translate) {


	$scope.colDefs = [
		{ field: 'productName', name: $translate.instant('NAME'), width:'10%', minWidth:100,  enableSorting: false, enableHiding: false,
			cellTemplate: '<div class="grid-name ui-grid-cell-contents"><a href="#/company/{{row.entity.companyCode}}/overview">{{row.entity[col.field]}}</a></div>'
		},
		{ field: 'establishDate' , name: $translate.instant('FOUNDED'), width:'8%', minWidth:80,
			cellTemplate:'<div class="grid-name ui-grid-cell-contents">'+
			'<span ng-hide="row.entity.establishDate != null">N/A</span>'+
			'<span ng-show="row.entity.establishDate != null">{{row.entity.establishDate.slice(0,7)}} </span>'+
			'</div>'
		},
		{ field: 'location' , name: $translate.instant('LOCATION'), width:'8%', minWidth:80, enableHiding: false},
		{ field: 'stage', name: $translate.instant('STAGE'), width:'8%', minWidth:80},
		{ field: 'funding', name: $translate.instant('FUNDING'), width:'20%', minWidth:200,
			cellTemplate:'<div class="ui-grid-cell-contents">'+
			'<span ng-repeat="item in row.entity.funding">' +
			' <a>{{item.fundingInvestment}} ~ ' +
			'<span ng-repeat="investor in item.investorList" ng-show="item.investorList.length>0">' +
			' {{investor.investor.investorName}}  </span> ' +
			'</a>' +
			'</span>'+
			'</div>'
		},
		{ field: 'companyFullName' , name: $translate.instant('FULL_NAME'), width:'18%', minWidth:200,  enableSorting: false, enableHiding: false
		},

		{ field: 'Odata', name: $translate.instant('OPERATING_DATA') , width:'25%'}
	];

	gridBasic($rootScope, $scope, $interval, $q, $cookieStore, 'ls_comps_select', compsGridService)

}


function CrowdfundingCtrl($scope, $http, crowdfundingService, cfTotalService) {
	$scope.page = 1;

	$http.get('./api/common/crowdfundingStatus').success(function(data){
		$scope.cfStatus = data.list;
	})

	$http.get('./api/common/crowdfundingSource').success(function(data){
		$scope.cfSource = data.list;
	})


	$http.get('./api/crowdfunding/getAll?page=1&status=all&source=all').success(function(data){
		$scope.cfList = data.cfList;
		$scope.total = data.total;

	})

	$scope.$watch(function(){return crowdfundingService.getData()}, function (newValue, oldValue) {
		if (newValue === oldValue) return;
		$scope.cfList = newValue;
	});

	$scope.$watch(function(){return cfTotalService.getData()}, function (newValue, oldValue) {
		if (newValue === oldValue) return;
		$scope.total = newValue;
	});

}


function CrowdfundingDetailCtrl($scope, $http, $stateParams) {
	var code = $stateParams.companyCode;

	$http.get('./api/crowdfunding/get?code='+code).success(function(data){
		$scope.cf = data.crowdfunding;

		var width = $scope.cf.successRaising / $scope.cf.amountRaising *100
		if (width > 100)
			width = 100;
		$('.first-line').css('width',width+'%')

		$scope.cf.successRaising = parseMoney($scope.cf.successRaising)
		$scope.cf.amountRaising = parseMoney($scope.cf.amountRaising)
	})


}


angular
    .module('gobi')
    .controller('MainCtrl', MainCtrl)
    .controller('TranslateCtrl', TranslateCtrl)
    .controller('HomeCtrl', HomeCtrl)
    .controller('SearchCtrl', SearchCtrl)
    .controller('ModalCtrl', ModalCtrl)
    .controller('ModalInstanceCtrl', ModalInstanceCtrl)
    //.controller('GridCtrl', GridCtrl)
    .controller('KeywordSwitchCtrl', KeywordSwitchCtrl)
    .controller('InvestorSwitchCtrl', InvestorSwitchCtrl)
    .controller('DatepickerCtrl', DatepickerCtrl)
    //.controller('CompanyHeadCtrl', CompanyHeadCtrl)
	.controller('CompanyTeamCtrl', CompanyTeamCtrl)
    .controller('CompanyEventsCtrl', CompanyEventsCtrl)
    .controller('BasicModalCtrl', BasicModalCtrl)
    .controller('BasicModalInstanceCtrl', BasicModalInstanceCtrl)
    .controller('EditModalCtrl', EditModalCtrl)
    .controller('EditModalInstanceCtrl', EditModalInstanceCtrl)
    .controller('SaveSearchCtrl', SaveSearchCtrl)
    .controller('ListCtrl', ListCtrl)
    .controller('ListDetailCtrl', ListDetailCtrl)
    .controller('ListModalCtrl', ListModalCtrl)
    //.controller('FollowCtrl', FollowCtrl)
	.controller('ListGridCtrl', ListGridCtrl)
	.controller('FollowGridCtrl', FollowGridCtrl)
    .controller('NewsCtrl', NewsCtrl)
    .controller('ThCtrl', ThCtrl)
	.controller('CompsCtrl', CompsCtrl)
	.controller('CompsGridCtrl', CompsGridCtrl)
	.controller('CrowdfundingCtrl', CrowdfundingCtrl)
	.controller('CrowdfundingDetailCtrl', CrowdfundingDetailCtrl)


    
    
    
