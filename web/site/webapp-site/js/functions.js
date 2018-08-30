/***** tools ******/
// date YYYY-MM-DD
function date2Timestap(date){
	var dateSplitted = date.split('-'); // date must be in DD-MM-YYYY format
	var formattedDate = dateSplitted[1]+'/'+dateSplitted[2]+'/'+dateSplitted[0];
	return new Date(formattedDate).getTime();
}



/** parse function**/
function parseAndStorage(model, value, $cookieStore){
	var bool = false;
	
	var storage = [];
	var storageKey = model;
	
	storage = $cookieStore.get(storageKey)
	if(storage == null) storage = [];
	if(storage.indexOf(value) == -1){
		storage.push(value);
		$cookieStore.put(storageKey, storage);
	}else
		bool = true;
    
    return bool;
}

function parseStorage(array){
	if(array == null) return;
	var storageString = '';
	
	angular.forEach(array, function(value, key) {
        storageString += value+ ' OR ';
	});
	storageString = storageString.slice(0, storageString.length-4);
	
	return storageString;
}

function parseStorageAndSwitch(array, switchSelect){
	if(array == null) return;
	var storageString = '';
	
	if(switchSelect == null || switchSelect == undefined) switchSelect = 'OR';
	else switchSelect = 'AND';
	
	angular.forEach(array, function(value, key) {
        storageString += value+ ' '+switchSelect+' ';
	});
	var min = switchSelect === 'OR'? 4:5;
	storageString = storageString.slice(0, storageString.length - min);
	
	return storageString;
}

function parseStage(array){
	if(array == null) return;
	var storageString = '';
	
	angular.forEach(array, function(value, key) {
		if(value == 'PRE_A') value = 'pre-A';
		if(value == 'LAST_STAGE') value = 'Last Stage';
		if(value == 'UNKNOWN') value = 'Unknown';
        storageString += value+ ' OR ';
	});
	storageString = storageString.slice(0, storageString.length-4);
	
	return storageString;
}

//to string
function parseStageValue(array){
	if(array == null) return;
	var storageString = '';
	
	angular.forEach(array, function(value, key) {
		
		if(value == 301) storageString += 'Angle'+ ' OR ';
		if(value == 302) storageString += 'Pre-A'+ ' OR '; 
		if(value == 303) storageString += 'Serials A'+ ' OR ';
		if(value == 304) storageString += 'Serials B'+ ' OR ';
		if(value == 305) storageString += 'Serials C'+ ' OR ';
		if(value == 306) storageString += 'Serials D'+ ' OR ';
		if(value == 307) storageString += 'Serials E'+ ' OR ';
		if(value == 308) storageString += 'Late Stage'+ ' OR ';
		if(value == 309) storageString += 'Pre-IPO'+ ' OR ';
		if(value == 310) storageString += 'IPO'+ ' OR ';
        
	});
	storageString = storageString.slice(0, storageString.length-4);
	
	return storageString;
}

function parseStageValue2(array){

	sValue = '';
	list = [];
	angular.forEach(array, function(value, key) {

		if(value == 301) sValue = 'Angle';
		if(value == 302) sValue = 'Pre-A';
		if(value == 303) sValue = 'A';
		if(value == 304) sValue = 'B';
		if(value == 305) sValue = 'C';
		if(value == 306) sValue = 'D';
		if(value == 307) sValue = 'E';
		if(value == 308) sValue = 'Late Stage';
		if(value == 309) sValue = 'Pre-IPO';
		if(value == 310) sValue = 'IPO';

		this.push(sValue)

	}, list);
	return list;
}



function parseFinance(value){
	if(value == null) return;
	var len = value.length;
    if(len > 9) value = value.substring(0, len-9)+'b';
    else if(len > 6) value = value.substring(0, len-6)+'m';
    else if(len > 3) value = value.substring(0, len-3)+'k';
    if(value == 100000000 || value == '100m') value = '100m+';
    
    return value;
}



function cookieComfirm($cookieStore, name){
	var value =  $cookieStore.get(name);
	if(value != null)
		$cookieStore.put('ls_'+name, value);
	else
		$cookieStore.put('ls_'+name, null);
}


function openModalFilter($rootScope, $scope, $http, $modal, $cookieStore, gridService, template){

	template = angular.lowercase(template);
    var modalInstance = $modal.open({
        animation: $scope.animationsEnabled,
        templateUrl: "./views/modal/"+ template + "_modal.html",
        controller: 'ModalInstanceCtrl'
    });
    
    modalInstance.result.then(function () {
    	$cookieStore.put('ls_page', 1);
    	change($rootScope, $scope, $http, $cookieStore, gridService);
    });

}


function appendElement(model, value){
	var result = '<div class="search-param label"> '
		+ value
	    + '<i class="fa fa-times close-filter" item-close-filter="'
        + model
        +'"></i>'
	    + '</div> ';
	
	return result;
}

function appendListSearch(selectedList){
	  var result =  '<div class="list-param label div-tag m-t-sm"  '+
	      'tooltip-placement="top" tooltip="Contains '+selectedList.companyCount+' Companies"'+
	      'select-list="'+selectedList.companyList.id+'">'+
	      selectedList.companyList.name+
	    '<i class="fa fa-plus"></i>'+
	    '</div>';
	  
	  return result;
	}


/**
 * filter rules change
 * 
 */
function change($rootScope, $scope, $http, $cookieStore, gridService){
	var params = getParams($rootScope, $scope, $cookieStore)
	$('.filter-selected').children('div').css('display', 'inline-block');
	loadSearchData($rootScope, $scope, $http, gridService, params);
}

function getParams($rootScope, $scope, $cookieStore){
	//search if change
	var change = $cookieStore.get('ls_change');
	if(!change) return;

	$scope.name = $cookieStore.get('ls_name');
	$scope.keyword = $cookieStore.get('ls_keyword');
	$scope.keywordSwitch = $cookieStore.get('ls_keyword_switch');
	$scope.location = $cookieStore.get('ls_location');
	$scope.investor = $cookieStore.get('ls_investor');
	$scope.investorSwitch = $cookieStore.get('ls_investor_switch');
	$scope.stage = $cookieStore.get('ls_stage');
	$scope.foundedAfter = $cookieStore.get('ls_founded_after');
	$scope.foundedBefore = $cookieStore.get('ls_founded_before');
	$scope.page = $cookieStore.get('ls_page');
	$scope.stageValue = $cookieStore.get('ls_stage_value');


	// to view
	$rootScope.nameSelected = parseStorage($scope.name);
	$rootScope.keywordSelected = parseStorageAndSwitch($scope.keyword, $scope.keywordSwitch);
	$rootScope.locationSelected =parseStorage($scope.location);
	$rootScope.investorSelected = parseStorageAndSwitch($scope.investor, $scope.investorSwitch);
	$rootScope.stageSelected = parseStage($scope.stage);
	$rootScope.foundedAfter = $scope.foundedAfter;
	$rootScope.foundedBefore = $scope.foundedBefore;
	
	var filter = {};
	filter.names = $scope.name;
	filter.keywords = $scope.keyword;
	filter.keywordSwitch = $scope.keywordSwitch;
	filter.locations = $scope.location;
	filter.investors = $scope.investor;
	filter.investorSwitch = $scope.investorSwitch;
	filter.stages = $scope.stageValue;
	
	var after = $scope.foundedAfter;
	if(after != null){
		after = after.slice(6,10)+'-'+after.slice(0,2)+'-'+after.slice(3,5);
	}
	var before = $scope.foundedBefore;
	if(before != null){
		before = before.slice(6,10)+'-'+before.slice(0,2)+'-'+before.slice(3,5);
	}
	
	filter.foundedAfter = after;
	filter.foundedBefore = before;
	filter.page = $scope.page==null?1 : $scope.page;



	//pageSize
	filter.pageSize = $cookieStore.get('ls_pageSize');
	if(filter.pageSize == 1)
		filter.page =1


	var params = angular.toJson(filter);
	console.log(params);
	$cookieStore.put('ls_params', params);
	
	$cookieStore.remove('ls_change');
	$cookieStore.remove('ls_pageSize');
	return params;
}


function loadSearchData($rootScope, $scope, $http, gridService, params){
	var req = {
	     method: 'POST',
	     url: '/api/search/company',
	     headers: {'Content-Type': 'application/json'},
	     data:  params,
	     responseType: 'json'
	    }

    var codeArr = [];

    $http(req)
        .success(function(data) {
          $rootScope.total = data.total;
          $scope.totalPage = data.total/100;

		  codeArr = data.companyIds;
        })
        .then(function(){

	      if(codeArr.length == 0){
            var data = [];
            gridService.newData(data);
            return;
          }
	      
          var reqDetail = {
               method: 'POST',
               url: pre_address+'/api/site/company/getCompanies',
               params: { codes: codeArr}
              }
              
         $http(reqDetail)
          .success(function(data) {
				 /** 此处可以解析 stage*/
             gridService.newData(data.companyList);
          })
        
      });
}

function exportExcel($rootScope, $scope, $http, $cookieStore){
	$cookieStore.put('ls_change', true);
	$cookieStore.put('ls_pageSize', 1);
	var params = getParams($rootScope, $scope, $cookieStore)
	getCompanyCodes($http, params)
}


function getCompanyCodes($http, params){
	var req = {
		method: 'POST',
		url: '/api/search/company',
		headers: {'Content-Type': 'application/json'},
		data:  params,
		responseType: 'json'
	}

	var codeArr = [];
	$http(req)
		.success(function(data) {
			codeArr =  data.companyIds;
		})
		.then(function(){
			if(codeArr.length == 0) return;
			var name = "export";

			var form = ('<form id="export-form" style="display: none"  action="./api/user/export/get" method="post">' +
				'<input name="codes" id="input-codes"/>' +
				'<input name="name" id="input-name"/>'+
				'</form>')

			$("#export").append(form);
			$("#input-codes").val(codeArr);
			$("#input-name").val(name);

			$("#export-form").submit();

		});
		
}


// Save search  --> parse
function parseSearchParams($filter, ele){
	ele.date = $filter('date')(ele.createTime, "yyyy-MM-dd HH:mm:ss");
	ele.params = angular.fromJson(ele.searchParams);
	ele.params.names = parseStorage(ele.params.names);
	ele.params.keywords = parseStorageAndSwitch(ele.params.keywords, ele.params.keywordSwitch);
	ele.params.locations = parseStorage(ele.params.locations);
	ele.params.investors = parseStorageAndSwitch(ele.params.investors, ele.params.investorSwitch);
	ele.params.stages = parseStageValue(ele.params.stages);
	
}



function keyUpOrDown(element, result, type){
	var list = result.children();
	if(list.length ==0 )return;
	
	var first = list.first();
	var last = list.last();
	
	var flag = false;
	var select;
	list.each(function(){
		if($(this).hasClass('result-select')){
			if(type=='up'){
				if($(this).children().text() == first.children().text())
					select = last;
				else
					select = $(this).prev();
				
			}
			else{
				if($(this).children().text() == last.children().text())
					select = first;
				else
					select = $(this).next();
			}
			flag = true;
		}
	}
	)
	
	
	if(!flag){
		
		if(type == 'up')
			select = element.parent().children('span').last().children().last();
		else
			select = element.parent().children('span').first().children().last();
	}
	
	if(type == 'down' && !flag){
		select = first;
	}
	
//	element.parent().children('span[class=tt-dropdown-menu]').css('display','block');
	
	select.addClass('result-select');
	select.siblings().removeClass('result-select');
	element.val((select.children().text()));
	return select;
}



function autoComplete(scope, element, model, $cookieStore, $compile){
	var value = element.text().trim();
	console.log(value)
    if(value == undefined || value == null || value =='')  return;
    var bool =parseAndStorage(model, value, $cookieStore);
//    scope.location = '';
    
    if(bool)
    	return;
	else{
		var el = $compile(appendElement(model, value))(scope);
		element.parent().parent().children('span').first().append(el);
		$cookieStore.put('ls_change', true);
	}
    $('#input-location').val('');
    $('#input-keyword').val('');
    $('#input-investor').val('');
    $('#input-name').val('');
    
    element.parent().css('display', 'none');
	element.siblings().removeClass('result-select');
    if(!$('#div-'+model).is(":visible"))
    	$('#div-'+model).css('display', 'inline-block');
}


function deleteOperation($http, element, model, id){
	
	var url= pre_address+'/api/site/user/';
	if(model == 'delete') url += 'search/delete';
	if(model == 'deleteOwner') url += 'list/deleteOwner';
	
	var req = {
			method: 'delete',
			url: url,
			params: {id : id}
	}
	
	$http(req).success(function(data){
		var div = "<div class='div-opearte-add pull-right'>" +
		"<i class='fa fa-check'></i>" +
		"<span>Delete Success</span>" +
		"</div>";
		
		var top = element.offset().top;
		
		element.parent().parent().parent().parent().append(div);
		$('.div-opearte-add').css({
			'top': top-23+'px',
			'right': '3%',
			'position': 'absolute'
			})
			.fadeIn(500).delay(1000).fadeOut(500);
		element.parent().parent().parent().fadeOut(1000);
		
	})
}

function comfirm($modal){
	   var modalInstance = $modal.open({
	        templateUrl: "./views/modal/user/comfirm_modal.html",
	        controller: 'BasicModalInstanceCtrl',
	        resolve: {
             template: function(){
             	return 'comfirm';
             }
         }
	    });
	   
	   return modalInstance;
}


// operate then alert success
function alertDiv(status, content){
	var div = "<div class='growl-container'>" +
		"<p>"+status+"</p>" +
		"<p>"+content+".</p>" +
		"</div>"
		$('#page-wrapper').append(div);
		$('.growl-container').delay(3000).fadeOut(500);
}

function alertDeleteDiv(status, content){
	var div = "<div class='growl-container'>" +
		"<p>"+status+"</p>" +
		"<p>"+content+".</p>" +
		"</div>"
		$('#page-wrapper').append(div);
		$('.growl-container').delay(3000).fadeOut(500);
}


function doSearch($rootScope, scope, $http, $location, $cookieStore, gridService, value, model){
	
	
    // clear old cookie;
	$cookieStore.remove('name');
	$cookieStore.remove('keyword');
	$cookieStore.remove('keyword_switch');
	$cookieStore.remove('location');
	$cookieStore.remove('investor');
	$cookieStore.remove('investor_switch');
	$cookieStore.remove('stage');
	$cookieStore.remove('stage_value');
	$cookieStore.remove('founded_after');
	$cookieStore.remove('founded_before');

    $cookieStore.remove('ls_name');
    $cookieStore.remove('ls_keyword');
    $cookieStore.remove('ls_keyword_switch');
    $cookieStore.remove('ls_location');
    $cookieStore.remove('ls_investor');
    $cookieStore.remove('ls_investor_switch');
    $cookieStore.remove('ls_stage');
	$cookieStore.remove('ls_stage_value');
    $cookieStore.remove('ls_founded_after');
    $cookieStore.remove('ls_founded_before');

	parseAndStorage(model, value, $cookieStore);
    var bool =parseAndStorage('ls_'+model, value, $cookieStore);
    if(bool) return;
    
    $('#top-search').val('');
    
    $cookieStore.put('ls_change', true);

    change($rootScope, scope, $http, $cookieStore, gridService);
    $location.path("/index/search");
}


function getAllList($scope, $http, $cookieStore, $location){
	
	$http.get(pre_address+'/api/site/user/list/getAll').success(function(data){
			$scope.allList = data.userList;
			$scope.total = $scope.allList.listCount;
			
		}).then(function(){
			var list = [];	
			if(	$cookieStore.get('ls_feature')){
				var id = $location.absUrl().split('?')[1];
				if(id == null || id =='') $location.path('/index/my_list');
				$http.get('./api/user/list/getFeature?companyId='+id).success(function(data){
					list = data.userList;
				}).then(function(){
					$cookieStore.remove('ls_feature');
				})
				
			}	
			else{
		        angular.forEach($scope.allList.companyListVOList, function(value, key){
		        		if(key < 10)
		        			this.push(value);
					}, list)
			}
			
			$scope.userList = list;
			if($scope.userList.length > 0)
				$('#list-in-modal').show();
		})
	
}


function gridBasic($rootScope, $scope, $interval, $q, $cookieStore, cookieName, listGridService){
	$rootScope.listSelectedCount = 0;

	var fakeI18n = function( title ){
		var deferred = $q.defer();
		$interval( function() {
			deferred.resolve( 'col: ' + title );
		}, 100, 1);
		return deferred.promise;
	};

	var windowHeigh = $( window ).height();
	var rows = 10;
	var num = (windowHeigh-240) / 40;
	rows = num > rows? num : rows;

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

				$cookieStore.put(cookieName, list);

				$rootScope.listSelectedCount = gridApi.grid.selection.selectedCount;
			});
			gridApi.selection.on.rowSelectionChangedBatch($scope,function(rows){

				var list = [];
				angular.forEach(gridApi.selection.getSelectedRows(), function(value, key){
					var code = value.companyCode;
					this.push(code);
				}, list)

				$cookieStore.put(cookieName, list);

				$rootScope.listSelectedCount = gridApi.grid.selection.selectedCount;
			});

		}

	};
	$scope.data = [];

	$scope.data = listGridService.getData();
	$rootScope.total = $scope.data.length;

	$scope.$watch(function(){return listGridService.getData()}, function (newValue, oldValue) {
		if (newValue === oldValue) return;

		$scope.gridApi.infiniteScroll.resetScroll();
		$scope.data = listGridService.getData();
	});


	$scope.$watch(function(){return $rootScope.listSelectedCount}, function (newValue, oldValue) {
		if (newValue === oldValue) return;
		$scope.gridApi.grid.selection.selectedCount = $rootScope.listSelectedCount;
	});
}

function setPageTitle(name){
	document.title = name +' | Gobi | Sedna';
}


function parseMoney(value){
	if(value == null) return;
	var len = value.length;
	if(len > 9)
		value = value.substring(0, len-9)+','+ value.substring(len-9, len-6)+','
				+value.substring(len-6, len-3)+','+ value.substring(len-3)
	else if(len > 6) value = value.substring(0, len-6)+','+value.substring(len-6, len-3)+','+ value.substring(len-3);
	else if(len > 3) value = value.substring(0, len-3)+','+ value.substring(len-3);

	return value;
}

function parseSourceInfo(source,sourceId){
	var sourceInfo={
		sourceUrl:null,sourceName:null
	}
	switch(source) {
		//Too do
		case 13010: sourceInfo.sourceUrl='http://dj.jd.com/funding/details/'+sourceId+'.html'; sourceInfo.sourceName='JD';break;
		//TO Do
		case 13020: sourceInfo.sourceUrl= 'https://rong.36kr.com/zhongchouDetail/'+sourceId;
			sourceInfo.sourceName='36kr';break;
		//TO Do
		case 13030: sourceInfo.sourceUrl= 'http://itjuzi.com/company/';break;
		case 13040: sourceInfo.sourceUrl= 'http://chuangyepu.com/startups/';break;
		case 13050: sourceInfo.sourceUrl= 'http://www.lagou.com/gongsi/';break;
		case 13051: sourceInfo.sourceUrl= 'neitui/company/';break;
		case 13052: sourceInfo.sourceUrl= 'http://www.jobtong.com/e/';break;
		case 13053: sourceInfo.sourceUrl= 'zhilian/company/';break;
		case 13054: sourceInfo.sourceUrl= 'zhilian/company/';break;
	}
	return sourceInfo;
}

function parseStatus(status){
	switch(status) {
		case '14010': return 'Ready';
		case '14020': return 'Raising';
		case '14030': return 'Closed';
	}
}

function parseRound(round){
	switch(round) {
		case 1010: return 'angel';
		case 1060: return 'D';
		case '14030': return 'Closed';
	}
}

function parseComSource(source,sourceId){
	var sourceInfo={
		sourceUrl:null,sourceName:null
	}
	switch(source) {
				//Too do
				case 13010: sourceInfo.sourceUrl='JD/company/';sourceInfo.sourceName='JD'; break;
				case 13020: sourceInfo.sourceUrl= 'https://rong.36kr.com/company/'+sourceId;sourceInfo.sourceName='36Kr';break;
				case 13030: sourceInfo.sourceUrl= 'http://itjuzi.com/company/'+sourceId;sourceInfo.sourceName='Itjuzi';break;
				case 13040: sourceInfo.sourceUrl= 'http://chuangyepu.com/startups/';sourceInfo.sourceName='chuangyepu';break;
				case 13050: sourceInfo.sourceUrl= 'http://www.lagou.com/gongsi/';sourceInfo.sourceName='Lagou';break;
				//Too do
				case 13051: sourceInfo.sourceUrl= 'neitui/company/';sourceInfo.sourceName='NeiTui';break;
				case 13052: sourceInfo.sourceUrl= 'http://www.jobtong.com/e/';break;
				//Too do
				case 13053: sourceInfo.sourceUrl= 'zhilian/company/';break;
				//Too do
				case 13054: sourceInfo.sourceUrl= 'zhilian/company/';break;
	}
	return sourceInfo;

}

function parseFollowStatus(status){

	switch(status) {

		case 1401: return 'New';
		case 1402: return 'Qualified';
		case 1403: return 'Negotiation';
		case 1404: return 'Active';
		case 1405: return 'Portfolio';
		case 1406: return 'Passed';

	}

}

function parseArtifactType(type){

	switch(type) {

		case 4010: return 'Website';
		case 4020: return 'Wechat';
		case 4030: return 'Weibo';
		case 4040: return 'Ios';
		case 4050: return 'Android';
		case 4060: return 'WindowsPhone';
		case 4070: return 'Pc';
		case 4080: return 'Mac';

	}

}