/**
 * pageTitle - Directive for set Page title - mata title
 */
function pageTitle($rootScope, $timeout) {
    return {
        link: function(scope, element) {
            var listener = function(event, toState) {
            	if(toState.name.indexOf('company') >-1) return;
            
                var title = 'Gobi | Sedna';
                if (toState.data && toState.data.pageTitle) title =  toState.data.pageTitle + ' | '+ title;

                $timeout(function() {
                    element.text(title);
                }, 0, false);

            };

            $rootScope.$on('$stateChangeStart', listener);
			//$rootScope.$on('$stateChangeSuccess', listener2);
        }
    }
};


/**
 * sideNavigation - Directive for run metsiMenu on sidebar navigation
 */
function sideNavigation($timeout) {
    return {
        restrict: 'A',
        link: function(scope, element) {
            // Call the metsiMenu plugin and plug it to sidebar navigation
            $timeout(function(){
                element.metisMenu();
            });
        }
    };
};


/**
 * minimalizaSidebar - Directive for minimalize sidebar
*/
function minimalizaSidebar($timeout, $cookieStore) {
    return {
        restrict: 'A',
        template: '<a class="navbar-minimalize minimalize-styl-2 btn btn-primary " href="" ng-click="minimalize()"><i class="fa fa-bars"></i></a>',
        controller: function ($scope, $element) {
            $scope.minimalize = function () {
                $("body").toggleClass("mini-navbar");
                if (!$('body').hasClass('mini-navbar') || $('body').hasClass('body-small')) {
                    // Hide menu in order to smoothly turn on when maximize menu
                    $('#side-menu').hide();
                    // For smoothly turn on menu
                    setTimeout(
                        function () {
                            $('#side-menu').fadeIn(500);
                        }, 100);
                    
                    $cookieStore.remove('ls_mini');
                    // grid auto size
                    
                } else if ($('body').hasClass('fixed-sidebar')){
                    $('#side-menu').hide();
                    setTimeout(
                        function () {
                            $('#side-menu').fadeIn(500);
                        }, 300);
                    
                } else {
                    // Remove all inline style from jquery fadeIn function to reset menu state
                    $('#side-menu').removeAttr('style');
                    $cookieStore.put('ls_mini', 'mini');
                }
            }
        }
    };
};


/**
 * icheck - Directive for custom checkbox icheck
 */
function icheck($timeout) {
    return {
        restrict: 'A',
        require: 'ngModel',
        link: function($scope, element, $attrs, ngModel) {
            return $timeout(function() {
                var value;
                value = $attrs['value'];

                $scope.$watch($attrs['ngModel'], function(newValue){
                    $(element).iCheck('update');
                })

                return $(element).iCheck({
                    checkboxClass: 'icheckbox_square-green',
                    radioClass: 'iradio_square-green'

                }).on('ifChanged', function(event) {
                        if ($(element).attr('type') === 'checkbox' && $attrs['ngModel']) {
                            $scope.$apply(function() {
                                return ngModel.$setViewValue(event.target.checked);
                            });
                        }
                        if ($(element).attr('type') === 'radio' && $attrs['ngModel']) {
                            return $scope.$apply(function() {
                                return ngModel.$setViewValue(value);
                            });
                        }
                    });
            });
        }
    };
}





/**
 * search filter - for *_modal.html
 */
function filter($rootScope, $http, $timeout, $location, $compile, $cookieStore, gridService) {
    return {
        restrict: 'AE',
        require: 'ngModel',
        transclude: true,
        
        link: function (scope, element, attrs, ngModel) {
        	element.bind("keydown", function(event) {
			var that = this;
    		var model = attrs.ngModel;

			//keydown hint
			element.next().css('display', 'block');

			if(event.keyCode === 229){
				return;
			}

    		if(event.which === 38){
    			keyUpOrDown(element, element.next(), 'up');
        		return;
        	}

    		if(event.which === 40){
    			keyUpOrDown(element, element.next(), 'down');
        		return;
        	}


            if(event.which === 13) {  
                scope.$apply(function(){
                	
                	var value = element.val();
                    if(value == undefined || value == null || value =='')  return;

					// full search
                	if(model == 'full'){
                		model = 'name';
                		
                		if(value.indexOf('in investor')>0){
                			model = 'investor';
                			value = value.slice(0, value.length-13);
                		}else if(value.indexOf('in keyword')>0){
                			model = 'keyword';
                			value = value.slice(0, value.length-12);
                		}
                		
                		doSearch($rootScope, scope, $http, $location, $cookieStore, gridService, value, model);
                		element.next().css('display', 'none');
						element.next().children().removeClass('result-select');
                		return;
                	}


                	
                    var bool =parseAndStorage(model, value, $cookieStore);
                    
                    if(model == 'keyword') scope.keyword = ''
                    if(model == 'location') scope.location = '';
                    if(model == 'investor') scope.investor = '';
                    if(model == 'name') scope.name = '';
                    
                    if(bool)
                    	return;
                	else{
                		var el = $compile(appendElement(model, value))(scope);
                		element.parent().children('span').first().append(el);
                	}
                    
                    element.next().css('display', 'none');
					element.next().children().removeClass('result-select');

                    if(!$('#div-'+model).is(":visible"))
                    	$('#div-'+model).css('display', 'inline-block');
                    
                    
                    if(model == 'keyword'){
	                    // add relation tags
	                	$http.get('./api/tag/rel/get?name='+value).success(function(data){
	                		if(data.tags.length > 0){
	                			$rootScope.relItems = data.tags;
	                			$('.tag-rel').show();
	                		}else{
	                			$('.tag-rel').hide();
	                		}
	                		
	                	})
                    }
                    
                    
                });  
                event.preventDefault();

              }
            
            });

			element.bind("keyup", function(event) {

				var keys = {
					ESC: 27,
					TAB: 9,
					RETURN: 13,
					LEFT: 37,
					UP: 38,
					RIGHT: 39,
					DOWN: 40
				};

				if(event.keyCode === keys.LEFT || event.keyCode === keys.RIGHT
					|| event.keyCode === keys.DOWN || event.keyCode === keys.UP)
					return;

				var value = element.val();
				if(value == '' || value ==null) return;

				var model = attrs.ngModel;

				var url = '/api/search/'+model;
				var req = {
					method: 'POST',
					url: url,
					data: value
				}

				$http(req)
					.success(function(data) {
						scope.ajaxKeywordItems = data.tags;
						scope.ajaxInvestorItems = data.investors;
						scope.ajaxLocationItems = data.locations;
						scope.ajaxNameItems =data.names;

						if( model == 'full'){
							var full = {};
							var tags = [];
							var investors = [];
							if(data.tags.length > 0)
								tags.push(data.tags[0]);
							else
								tags = null;

							if(data.investors.length > 0)
								investors.push(data.investors[0])
							else
								investors = null;

							full.tags = tags;
							full.investors = investors;
							full.names = data.names;

							scope.ajaxFullItems = full;
						}


					})
			});

        	element.bind("click", function(event) {
        		if(attrs.ngModel == 'full')
        			$('.search-span').show();

				if(attrs.ngModel == 'add' && $("#add-company").val() != "")
					$('.name-result-span').show();
        		
        		event.stopPropagation();
        	});
        	
        	element.bind("focusout", function(event) {
        		//element.next().css('display', 'none');
        	})
        }
    }
}



/**
 *  Close click event
 */
function closeFilter($rootScope, $http, $cookieStore, gridService){
	 return {
	        restrict: 'AE',
	        link: function (scope, element, attrs) {
	        	element.bind("click", function(event) {
	        		element.parent().hide();
	        		var close = attrs.closeFilter;
	        		$cookieStore.remove('ls_'+attrs.closeFilter);
					$cookieStore.remove(attrs.closeFilter);
	        		if(close == 'stage'){
	        			$cookieStore.remove('ls_stage_value');
						$cookieStore.remove('stage_value');
						$cookieStore.remove('stage');
	        		}
	        		if(close == 'founded') {
	        			$cookieStore.remove('ls_founded_after');
	        			$cookieStore.remove('ls_founded_before');
						$cookieStore.remove('founded_after');
						$cookieStore.remove('founded_before');
	        		}
	        		
	        		
	        		$cookieStore.put('ls_change', true);
	        		// load data
	        		$cookieStore.put('ls_page', 1);
	        		change($rootScope, scope, $http, $cookieStore, gridService);
	        	});
	        }
	    }
}

/**
 * close item in modal
 * 
 */
function itemCloseFilter($rootScope, $cookieStore){
    return {
        restrict: 'AE',
        link: function (scope, element, attrs) {
            element.bind("click", function(event) {
                element.parent().remove();
                var model = attrs.itemCloseFilter;
                var varable = attrs.itemCloseFilter;
                var storage = $cookieStore.get(varable);
                var value = element.parent().text().trim();
                //storage.pop(value);
                for (var i = storage.length; i--;) {
    		        if (storage[i] === value) 
    		        	storage.splice(i, 1);
    		    }
                
                if(storage.length == 0)
                	$cookieStore.remove(varable);
                else
                	$cookieStore.put(varable, storage);
                
                //$cookieStore.put('ls_change', true);
            });
            
        }
    }
}

function stageFilter($cookieStore){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("click", function(event) {
        		
        		var checked = element.context.checked;
        		var ls_stage = [];
        		var ls_stage_value = [];
        		var storage = $cookieStore.get('ls_stage');
        		var storageValue = $cookieStore.get('ls_stage_value');
        		if(storage != null) ls_stage = storage;
        		if(storageValue != null) ls_stage_value = storageValue;
        		
        		var name = attrs.ngValue;
        		var value = attrs.stageFilter;

        		if(checked) {
        			ls_stage.push(name);
        			ls_stage_value.push(value);
        		}
        		else {
        			for (var i = ls_stage.length; i--;) {
        		        if (ls_stage[i] == name)
        		        	ls_stage.splice(i, 1);
        		    }
        			
        			for (var i = ls_stage_value.length; i--;) {
        		        if (ls_stage_value[i] == value)
        		        	ls_stage_value.splice(i, 1);
        		    }
        		}



        		if(ls_stage.length != 0)
        			//$cookieStore.remove('ls_stage');
        		//else
        			$cookieStore.put('stage', ls_stage);
				else
					$cookieStore.remove('stage');
        		
        		if(ls_stage_value.length != 0)
        		//	$cookieStore.remove('ls_stage_value');
        		//else
        			$cookieStore.put('stage_value', ls_stage_value);
				else
					$cookieStore.remove('stage_value');


				cookieComfirm($cookieStore, 'stage');
				cookieComfirm($cookieStore, 'stage_value');

        	});
        }
    }
}


function foundedFilter($cookieStore){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("focusout", function(event) {
        		var type = attrs.foundedFilter;
        		var value = element.val();
        		if(type=='after')
        			//$cookieStore.put('ls_founded_after', value);
					$cookieStore.put('founded_after',value)

        		else
        			//$cookieStore.put('ls_founded_before', value);
					$cookieStore.put('founded_before', value);
        		
        	});
        }
    }
}


//search 
function search($rootScope, $cookieStore, $http, $location, $compile, gridService){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("click", function(event) {
        		var value = element.children('span').first().text().trim();
        	    if(value == undefined || value == null || value =='')  return;
        		doSearch($rootScope, scope, $http, $location, $cookieStore, gridService, value, attrs.search);
        		element.parent().css('display', 'none');
				element.siblings().removeClass('result-select');
    		});
        }
    }
}


function searchKeyword($rootScope, $http, $location, $cookieStore, gridService){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("click", function(event) {
        		var value = element.text().trim();
        	    if(value == undefined || value == null || value =='')  return;
        		doSearch($rootScope, scope, $http, $location, $cookieStore, gridService, value, 'keyword');
        	});
        }
	}
}

function searchInvestor($rootScope, $http, $location, $cookieStore, gridService){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("click", function(event) {
        		var value = element.text().trim();
        	    if(value == undefined || value == null || value =='')  return;
        		doSearch($rootScope, scope, $http, $location, $cookieStore, gridService, value, 'investor');
        	});
        }
	}
}



//AJAX auto Complete in modal page
function nameAutoComplete($rootScope, $cookieStore, $http, $compile){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("click", function(event) {
        		autoComplete(scope, element, 'name', $cookieStore, $compile);
        	});
        }
    }
}


function keywordAutoComplete($rootScope, $cookieStore, $http, $compile){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("click", function(event) {
        		autoComplete(scope, element, 'keyword', $cookieStore, $compile);
        		
        		var value = element.text().trim();
        		$http.get('./api/tag/rel/get?name='+value).success(function(data){
            		if(data.tags.length > 0){
            			$rootScope.relItems = data.tags;
            			$('.tag-rel').show();
            		}else{
            			$('.tag-rel').hide();
            		}
            		
            		
            	})
        	
        	});
        }
    }
}

function investorAutoComplete($cookieStore, $compile){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("click", function(event) {
        		autoComplete(scope, element, 'investor', $cookieStore, $compile);
        	});
        }
    }
}


function locationAutoComplete($cookieStore, $compile){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("click", function(event) {
        		autoComplete(scope, element, 'location', $cookieStore, $compile);
        	});
        }
    }
}



// add class
function categoryFilter(){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("click", function(event) {
        		element.parent().addClass('cate-active');
        		element.parent().siblings().removeClass('cate-active');
        	});
        }
    }
}

function followFilter(){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("click", function(event) {
        		element.addClass('cate-active');
        		element.siblings().removeClass('cate-active');
        	});
        }
    }
}


function deleteSavedSearch($http){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("click", function(event) {
        		deleteOperation($http, element, 'delete', attrs.deleteSavedSearch);
        	});
        }
    }
}

function deleteOwner($http, $modal){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("click", function(event) {
        		
        		var modalInstance = comfirm($modal);
        		 modalInstance.result.then(function (callBack) {
        			 if(callBack.comfirm){
        				deleteOperation($http, element, 'deleteOwner', attrs.deleteOwner);
        			 }
    			 });
        	
        	});
        }
    }
}


/**
 * load more data
 */
function loadMoreData($rootScope, $http, $filter){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("click", function(event) {
        		var model = attrs.loadMoreData;
        		
        		var url = '';
        		if(model == 'search'){
        			url = './api/user/search/get';
        			scope.page = scope.searchList.length/20;
        		}
        		if(model == 'list'){
        			url = './api/user/list/get';
        			scope.page = scope.userList.length/20;
        		}
				if(model == 'tech_news'){
					url = '/api/news/tech';
					scope.page = scope.techNewsList.length/20;
				}


        		var req = {
        				 method: 'get',
        				 url: url,
        				 params: { page: ++scope.page}
        		    }

				if(model == 'cf'){
					url = './api/crowdfunding/getAll';
					scope.page = scope.cfList.length/20;

					var statusList = $('#cfStatus').children();
					var sourceList = $('#cfSource').children();
					var status = '';
					var source = '';

					statusList.each(function(){
						if($(this).hasClass('selected-bg')){
							status = $(this).attr("cf-status")
						}
					})

					sourceList.each(function(){
						if($(this).hasClass('selected-bg')){
							source = $(this).attr("cf-source")
						}
					})

					$http.get(url+'?page='+(++scope.page)+'&status='+status+'&source='+source).success(function(data){
						scope.total = data.total;
						scope.cfList = scope.cfList.concat(data.cfList);
					})

					return;
				}
        		
        		$http(req).success(function(data){
        			scope.total = data.total;
        			var list = [];
        			if(model == 'search'){
	        			angular.forEach(data.searchList, function(value, key){
	        				var ele = {};
	        				ele = value;
	        				parseSearchParams($filter, ele);
	        				
	        				this.push(ele);
	        			}, list)
	        			
	        			list = data.searchList;
	        			scope.searchList = scope.searchList.concat(list);
        			}
        			
        			if(model == 'list'){
        				scope.userList = scope.userList.concat(data.userList);
        			}

					if(model == 'tech_news'){
						scope.techNewsList = scope.techNewsList.concat(data.result);

						scope.techNewsList.sort(function(a, b) {
							var result =  new Date(b.news.newsDate) - new Date(a.news.newsDate)
							return result
						});
					}


        		})
        	});
        }
    }
}


// list modal
function loadMoreList($rootScope, $http, $filter){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("click", function(event) {
        		var list = [];
        		var page = scope.userList.length/20;
        		
        		
        		angular.forEach(scope.allList, function(value, key){
            		if(key >= page*20 && key < (page+1)*20)
            			this.push(value);
    			}, list)
    			
    			scope.userList = scope.userList.concat(list);
        	})
        }
	}
}



/**
 * list modal 
 * select list to save
 */
function selectList($cookieStore){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("click", function(event) {
        		var id = attrs.selectList;
        		// single select
        		$('.div-tag').removeClass('bg-selected');
        		element.addClass('bg-selected');
        		
        		
//        		var list = $cookieStore.get('ls_add_list');
//        		
//        		if(list == null) list = [];
//        		if(list.indexOf(id) == -1)
//        			list.push(id);
//        		else{
//        			 for (var i = list.length; i--;) {
//         		        if (list[i] === id) 
//         		        	list.splice(i, 1);
//         		    }
//        		}
        		
        		var list= [];
        		list.push(id);
        		
        		$cookieStore.put('ls_add_list', list);
        		
        	});
        }
    }
}

/**
 * my list page 
 * list desc focusout save
 * 
 */
function listDesc($http){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("focusout", function(event) {
        		var list = angular.fromJson(attrs.listDesc);
        		var old = list.listDesc;
        		
        		var desc = element.val();
        		if(old == desc) return;
        		
        		//save desc
        		var req = {
       				 method: 'put',
       				 url: './api/user/list/updateDesc',
       				 params: { desc: desc, id: list.listId}
       		    }
       		
		   		$http(req).success(function(data){
		   			
		   		})
        		
        	})
        }
    }
}


/**
 * company page 
 * add heart
 *  
 */

function companyHeart($http, $modal, $stateParams){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("click", function(event) {
        		
				var code =$stateParams.companyCode;
        		
        		if(element.hasClass('fa-heart')){
        			
        			var modalInstance = comfirm($modal);
	           		 modalInstance.result.then(function (callBack) {
	           			 if(callBack.comfirm){
	           				var req = {
	                 				 method: 'put',
	                 				 url: './api/user/company/updateHeart',
	                 				 params: { code: code, heart: 'N'}
	                 		    }
	                 		
	          		   		$http(req).success(function(data){
	          		   			
	          		   		}).then(function(){
	          		   			element.removeClass('fa-heart');
	          		   			element.addClass('fa-heart-o');
	          		   		})
	          		   		
	           			 }
	           		 });
        			
        			
        		}else{
        			
        			//update heart
        			var req = {
              				 method: 'put',
              				 url: './api/user/company/updateHeart',
              				 params: { code: code, heart: 'Y'}
              		    }
              		
       		   		$http(req).success(function(data){
       		   			
       		   		}).then(function(){
       		   			element.removeClass('fa-heart-o');
       		   			element.addClass('fa-heart');
       		   		})
        			
        		}
        	})
        }
	}
}


/**
 * search page
 * new search
 */ 
function newSearch($cookieStore, $http, $location, $rootScope){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("click", function(event) {
        		var id = attrs.newSearch;
        		
        		$http.get('./api/user/search/getById?id='+id).success(function(data){
        			var params = angular.fromJson(data.search.searchParams);

					params.stagesValue = params.stages;
					params.stages = parseStageValue2(params.stages);
					if(params.stages.length == 0) params.stages = null

					//cookie restore
					$cookieStore.put('name', params.names==null?null:params.names);
					$cookieStore.put('keyword', params.keywords==null?null:params.keywords);
					$cookieStore.put('location', params.locations==null?null:params.locations);
					$cookieStore.put('investor', params.investors==null?null:params.investors);
					$cookieStore.put('stage', params.stages);
					$cookieStore.put('stage_value', params.stagesValue==null?null:params.stagesValue);
					$cookieStore.put('founded_after', params.foundedAfter==null?null:params.foundedAfter);
					$cookieStore.put('founded_before', params.foundedBefore==null?null:params.foundedBefore);



        			$cookieStore.put('ls_name', params.names==null?null:params.names);
            		$cookieStore.put('ls_keyword', params.keywords==null?null:params.keywords);
            		$cookieStore.put('ls_keyword_switch', params.keywordSwitch==null?null:params.keywordSwitch);
            		$cookieStore.put('ls_location', params.locations==null?null:params.locations);
            		$cookieStore.put('ls_investor', params.investors==null?null:params.investors);
            		$cookieStore.put('ls_investor_switch', params.investorSwitch==null?null:params.investorSwitch);
            		$cookieStore.put('ls_stage', params.stages);
					$cookieStore.put('ls_stage_value', params.stagesValue==null?null:params.stagesValue);
            		$cookieStore.put('ls_founded_after', params.foundedAfter==null?null:params.foundedAfter);
            		$cookieStore.put('ls_founded_before', params.foundedBefore==null?null:params.foundedBefore);

					//getParams($rootScope, scope, $cookieStore);

//            		$cookieStore.put('ls_page', params.page);
            		
        		}).then(function(){
        			$location.path("/index/search");

					$("#li-search").addClass('active')
							.siblings().removeClass('active');
        		})
        		
        		
        		
        		
        	})
        }
    }
}


function similarAddList($http, $modal, $cookieStore, $translate){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("click", function(event) {
        		 var list = [];
        		 list.push(attrs.similarAddList);
        		 $cookieStore.put('ls_select_rows',list);
        		 
        		 $cookieStore.remove('ls_add_list');
				 var modalInstance =  $modal.open({
				        templateUrl: "./views/modal/user/list_modal.html",
				        controller: 'BasicModalInstanceCtrl',
				        resolve: {
			             template: function(){
			             	return 'list';
			             }
			         }
				    });
				 modalInstance.result.then(function (callBack) {
					 
					 console.log(callBack.list);
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
				 });
			 
        	})
        }
	}
}


function selectRow(){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("mouseenter", function(event) {
        		scope.$apply(function(){
        			element.addClass('bg-selected-row');
        			element.siblings().removeClass('bg-selected-row');
        		})
        	})
        	element.bind("mouseleave", function(event) {
        		scope.$apply(function(){
        			element.removeClass('bg-selected-row');
        		})
        	})
        }
	}
}

function createList($http, $modal, $cookieStore, $location, $translate){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("click", function(event) {
        		var listName = $('#list-name').val().trim();
        		if(listName == null || listName== ''){
        			$('#list-name').focus();
        			return;
        		}
        		
        		var req = {
        				 method: 'put',
        				 url: './api/user/list/create',
        				 params: { name: listName}
        		    }
        		
           		$http(req).success(function(data){
           		}).then(function(){
           			getAllList( scope, $http, $cookieStore, $location);
           			
           			//add to selected list
//           		$('.list-param').first().addClass('bg-selected');
//           		var list= [];
//            		list.push(id);
//            		$cookieStore.put('ls_add_list', list);
           			
           			$('#hide-create-list').hide();
           			$('#div-create-list').hide();
           			$('#a-create-list').show();
           			alertDiv($translate.instant('SAVED'), $translate.instant('CREATE_NEW_LIST_SUCCESS'));
			   		
           		})
			 
        	})
        }
	}
}


function addList($http, $modal, $cookieStore, $translate){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("click", function(event) {
        		$cookieStore.put('ls_feature', true);
        		var modalInstance =  $modal.open({
				        templateUrl: "./views/modal/user/list_modal.html",
				        controller: 'BasicModalInstanceCtrl',
				        resolve: {
			             template: function(){
			             	return 'list';
			             }
			         }
				    });
				 modalInstance.result.then(function (callBack) {
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
				 });
			 
        	})
        }
	}
}


/**
 * list search filter - for list_modal.html
 */
function listFilter($rootScope, $http, $timeout, $location, $compile, $cookieStore, gridService) {
    return {
        restrict: 'A',
        transclude: true,
        link: function (scope, element, attrs, ngModel) {
        	element.bind("keyup", function(event) {
        	var select = '';
    		if(event.which==32){
    	       return;
    	    }
    		if(event.which === 38){
    			select = keyUpOrDown(element, element.next(), 'up');
    			element.val((select.children().first().text().trim()));
        		return;
        	}
    		
    		if(event.which === 40){
    			select = keyUpOrDown(element, element.next(), 'down');
    			element.val((select.children().first().text().trim()));
        		return;
        	}
        		
        	// AJAX auto complete
        	var val = element.val().trim();
        	if(val == '' || val ==null) return;
        	
        	
        	scope.searchList = [];
        	
        	$http.get('./api/user/list/search').success(function(data){
        		var i=0;
    	        angular.forEach(scope.allList, function(value, key){
    	        		if(angular.lowercase(value.listName).indexOf(angular.lowercase(val)) > -1 && i <8){
    	        			this.push(value);
    	        			i++;
    	        		}
    				}, scope.searchList)
        	})
				
			
        	//list hint
        	$('.list-search-dropdown').css('display', 'block');
        	
        	 if(event.which === 13) {  
                 scope.$apply(function(){
                 	
                 	var value = element.val();
                    if(value == null || value =='')  return;
                 	
                    
                    var resultList = $('.list-search-dropdown').children();
                    var flag =false;
                    resultList.each(function(){
                		if($(this).hasClass('result-select')){
                			select = $(this);
                			flag = true;
                		}
                	})
                	
                	$('.list-search-result').children().remove();
                	if(flag){
                		var listId = select.children('input').val();
                		var selectedList = {};
                		angular.forEach(scope.allList, function(v, key){
        	        		if(v.listId == listId){
        	        			selectedList = v;
        	        		}
        				})
        				
        				var el = $compile(appendListSearch(selectedList))(scope);
//                		el.addClass('bg-selected');
                		$('.list-search-result').append(el);
                	}else{
                		var searchResult =[];
                		var i = 0 ;
                		angular.forEach(scope.allList, function(v, key){
        	        		if(v.listName.indexOf(value) > -1 && i<8){
        	        			var el = $compile(appendListSearch(v))(scope);
                        		$('.list-search-result').append(el);
                        		this.push(v);
                        		i++;
        	        		}
        				}, searchResult);
        				
                	}
                    
                    $('.list-search-dropdown').css('display', 'none');
                 });  
                 event.preventDefault();
               }
             
             });
        	element.bind("click", function(event) {
        		var val = element.val().trim();
            	if(val == '' || val ==null) return;
    			$('.list-search-dropdown').show();
        		
        		event.stopPropagation();
        	});
        }
    }
}



function listAutoComplete($compile){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("click", function(event) {
        		var listId = attrs.listAutoComplete;
        		var selectedList = {};
        		angular.forEach(scope.allList, function(v, key){
	        		if(v.listId == listId){
	        			selectedList = v;
	        		}
				})
				
				var el = $compile(appendListSearch(selectedList))(scope);
//        		el.addClass('bg-selected');
        		$('.list-search-result').append(el);
        		$('.list-search-dropdown').css('display', 'none');
        	});
        }
    }
}


function navHref($window){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("click", function(event) {
//        		element.parent().addClass('active');
//        		element.parent().siblings().removeClass('active');
        		
        		var href = attrs.navHref;
        		
        		var li;
        		
        		if(href == 'home'){
        			li = $('#li-home');
        			$window.location.href = '#/index/home';
        		}
        		else if(href == 'search'){
        			li = $('#li-search');
        			$window.location.href = '#/index/search';
        		}
        		else if(href == 'searches'){
        			li = $('#li-searches');
        			$window.location.href = '#/index/searches';
        		}
        		else if(href == 'list'){
        			li = $('#li-list');
        			$window.location.href = '#/index/my_list';
        		}
        		
        		if(li != null){
	        		li.addClass('active');
	        		li.siblings().removeClass('active');
        		}
        		
        	})
        }
	}
}


function toTop(){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("click", function(event) {
        		$(document.body).animate({'scrollTop':0},100);
        	})
        }
	}
}

function companyPopover(){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	element.bind("mouseenter", function(event) {
        		element.next().show();
        	})
        	element.bind("mouseleave", function(event) {
        		element.next().hide();
        	})
        	
        	element.next().bind("mouseenter", function(event) {
        		element.next().show();
        	})
        	
        	element.next().bind("mouseleave", function(event) {
        		element.next().hide();
        	})
        }
	}
}


function eventPopover(){
	return {
		restrict: 'A',
		link: function (scope, element, attrs) {
			element.bind("mouseenter", function(event) {
				element.next().show();
				//element.css('color','#179d82');
			})
			element.bind("mouseleave", function(event) {
				element.next().hide();
				//element.css('color','#000');
			})

			element.next().bind("mouseenter", function(event) {
				element.next().show();
				//element.css('color','#179d82');
			})

			element.next().bind("mouseleave", function(event) {
				element.next().hide();
				//element.css('color','#000');
			})
		}
	}
}


function memberDisplay(){
	return {
		restrict: 'A',
		link: function (scope, element, attrs) {
			element.bind("mouseenter", function(event) {
				element.find('div.member-info').addClass('display-block')
			})
			element.bind("mouseleave", function(event) {
				element.find('div.member-info').removeClass('display-block')
			})
		}
	}
}


function showAll(){
	return {
		restrict: 'A',
		link: function (scope, element, attrs) {
			element.bind("click", function(event) {
				element.parent().find('div.row').addClass('display-block')
				element.hide()
			})
			//element.bind("mouseleave", function(event) {
			//	element.parent().find('div.row').removeClass('display-block')
			//})
		}
	}
}





function thSelect($cookieStore){
	return {
        restrict: 'A',
        link: function (scope, element, attrs) {
        	
        	element.bind("click", function(event) {
        		
        		var id = attrs.thSelect;
        		
        		if(element.hasClass('bg-default')){
        			var special = $cookieStore.get('th_special');
            		if(special == null) special =[];
            		
            		special.push(id);
            		element.addClass('bg-special');
            		element.removeClass('bg-default');
            		
            		$cookieStore.put('th_special', special);
        		}
        		
        		else if(element.hasClass('bg-special')){
        			var using = $cookieStore.get('th_using');
            		if(using == null) using =[];
            		using.push(id);
            		element.addClass('bg-using');
            		element.removeClass('bg-special');
            		$cookieStore.put('th_using', using);
            		
            		var special = $cookieStore.get('th_special');
            		for (var i = special.length; i--;) {
          		        if (special[i] === id) 
          		        	special.splice(i, 1);
          		    }
            		$cookieStore.put('th_special', special);
            		
        		}
        		
        		else if(element.hasClass('bg-using')){
        			var waste = $cookieStore.get('th_waste');
            		if(waste == null) waste =[];
            		
            		waste.push(id);
            		element.addClass('bg-waste');
            		element.removeClass('bg-using');
            		
            		$cookieStore.put('th_waste', waste);
            		
            		var using = $cookieStore.get('th_using');
            		for (var i = using.length; i--;) {
          		        if (using[i] === id) 
          		        	using.splice(i, 1);
          		    }
            		$cookieStore.put('th_using', using);
        		}
        		
        		else if(element.hasClass('bg-waste')){
            		element.addClass('bg-default');
            		element.removeClass('bg-waste');

            		var  waste = $cookieStore.get('th_waste');
            		for (var i = waste.length; i--;) {
          		        if (waste[i] === id) 
          		        	waste.splice(i, 1);
          		    }
            		$cookieStore.put('th_waste', waste);
        		}
        		
        	})
        }
	}
}


function addCompany($rootScope, $http, $timeout, $location, $cookieStore){
	return {
		restrict: 'AE',
		transclude: true,

		link: function (scope, element, attrs) {
			element.bind("keydown", function(event) {
				var that = this;

				//keydown hint
				$('.name-result-span').css('display', 'block');

				if(event.keyCode === 229){
					return;
				}

				if(event.which === 38){
					keyUpOrDown(element, element.next().next(), 'up');
					return;
				}

				if(event.which === 40){
					keyUpOrDown(element, element.next().next(), 'down');
					return;
				}

				if(event.which === 13) {

						var value = element.val();
						if(value == undefined || value == null || value =='')  return;
						scope.name = '';

						$(".name-result-span").css('display', 'none');
						$(".name-result-span").removeClass('result-select');
				}
			});


			element.bind("keyup", function(event) {

				var keys = {
					ESC: 27,
					TAB: 9,
					RETURN: 13,
					LEFT: 37,
					UP: 38,
					RIGHT: 39,
					DOWN: 40
				};

				if(event.keyCode === keys.LEFT || event.keyCode === keys.RIGHT
					|| event.keyCode === keys.DOWN || event.keyCode === keys.UP)
					return;

				var value = element.val();
				if(value == '' || value ==null) return;


				// AJAX auto complete
				var value = element.val();

				var url = '/api/search/name';
				var req = {
					method: 'POST',
					url: url,
					data: value
				}

				$http(req)
					.success(function(data) {
						scope.ajaxNameItems =data.names;
					})
			});

			element.bind("click", function(event) {

				if(attrs.ngModel == 'add' && $("#add-company").val() != "")
					$('.name-result-span').show();

				event.stopPropagation();
			});

		}
	}
}


function compsAutoComplete($cookieStore, $compile){
	return {
		restrict: 'A',
		link: function (scope, element, attrs) {
			element.bind("click", function(event) {
				$("#add-company").val(element.text().trim());
			});
		}
	}
}


function cfStatus($rootScope, $http, crowdfundingService, cfTotalService){
	return {
		restrict: 'A',
		link: function (scope, element, attrs) {
			element.bind("click", function(event) {
				var model = attrs.cfStatus;
				if (element.hasClass('selecte-bg'))
					return

				element.addClass('selected-bg')
					.siblings().removeClass('selected-bg')

				list = $("#cfSource").children();
				source = 'All'
				list.each(function(){
						if($(this).hasClass('selected-bg')){
							source = $(this).attr("cf-source")
						}
					}
				)
				
				$http.get('./api/crowdfunding/getAll?page=1&status='+model+'&source='+source).success(function(data){
					scope.cfList = data.cfList;
					scope.total = data.total;
					crowdfundingService.newData(scope.cfList)
					cfTotalService.newData(scope.total)
				})
			});
		}
	}
}


function cfSource($rootScope, $http, crowdfundingService, cfTotalService){
	return {
		restrict: 'A',
		link: function (scope, element, attrs) {
			element.bind("click", function(event) {
				var model = attrs.cfSource;
				if (element.hasClass('selecte-bg'))
					return

				element.addClass('selected-bg')
					.siblings().removeClass('selected-bg')

				list = $("#cfStatus").children();
				status = 'All'
				list.each(function(){
						if($(this).hasClass('selected-bg')){
							status = $(this).attr("cf-status")
						}
					}
				)

				$http.get('./api/crowdfunding/getAll?page=1&source='+model+'&status='+status).success(function(data){
					scope.cfList = data.cfList;
					scope.total = data.total;
					crowdfundingService.newData(scope.cfList)
					cfTotalService.newData(scope.total)
				})
			});
		}
	}
}


/**
 *
 * Pass all functions into module
 */
angular
    .module('gobi')
	.directive('pageTitle', pageTitle)
    .directive('sideNavigation', sideNavigation)
    .directive('minimalizaSidebar', minimalizaSidebar)
    .directive('icheck', icheck)
    
    .directive('filter', filter)
    .directive('closeFilter', closeFilter)
    .directive('itemCloseFilter', itemCloseFilter)
    .directive('stageFilter', stageFilter)
    .directive('foundedFilter', foundedFilter)
    .directive('search', search)
    .directive('searchKeyword', searchKeyword)
    .directive('searchInvestor', searchInvestor)
    .directive('nameAutoComplete', nameAutoComplete)
    .directive('keywordAutoComplete', keywordAutoComplete)
    .directive('investorAutoComplete', investorAutoComplete)
    .directive('locationAutoComplete', locationAutoComplete)
    .directive('categoryFilter', categoryFilter)
    .directive('followFilter', followFilter)
    .directive('deleteSavedSearch', deleteSavedSearch)
    .directive('deleteOwner', deleteOwner)
    .directive('loadMoreData', loadMoreData)
    .directive('loadMoreList', loadMoreList)
    .directive('selectList', selectList)
    .directive('listDesc', listDesc)
    .directive('companyHeart', companyHeart)
    .directive('newSearch', newSearch)
    .directive('similarAddList', similarAddList)
    .directive('selectRow', selectRow)
    .directive('createList', createList)
    .directive('addList', addList)
    .directive('listFilter', listFilter)
    .directive('listAutoComplete', listAutoComplete)
    .directive('navHref', navHref)
    .directive('toTop', toTop)
    .directive('companyPopover', companyPopover)
	.directive('eventPopover', eventPopover)
	.directive('memberDisplay', memberDisplay)
	.directive('showAll', showAll)
    .directive('thSelect', thSelect)
	.directive('addCompany', addCompany)
	.directive('compsAutoComplete', compsAutoComplete)
	.directive('cfStatus', cfStatus)
	.directive('cfSource', cfSource)

    
