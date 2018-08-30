/**
 * Created by haiming on 15/12/10.
 */

/**
 * ModalCtrl
 */
angular.module('gobi')
    .controller('ModalCtrl', ModalCtrl)
    .controller('SearchCtrl', SearchCtrl)
    .controller('GridCtrl', GridCtrl)


function ModalCtrl($rootScope, $scope, $http, $modal, $log, $cookieStore, gridService) {
    $http.get(pre_address+'/api/site/common/searchBy').success(function(data){
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
    /**
    * row 是默认展示的列数目，num是根据窗口大小来调整展示的列数目
    * */
    var windowHeigh = $( window ).height();
    var rows = 10;
    var num = (windowHeigh-230) / 40;
    rows = num > rows? num : rows;
/**
 * 定义展示的规范和内容
 * */
    $scope.colDefs = [
        { field: 'name', name: $translate.instant('NAME'), width:'17%', minWidth:100,  enableSorting: false, enableHiding: false,
            cellTemplate: '<div class="grid-name ui-grid-cell-contents">' +

            '<a href="#/company/{{row.entity.company.code}}/overview">{{row.entity.company.name}}</a>' +
            '<span class="grid-verify" ng-show="row.entity.company.verify == '+"'Y'"+'">{{"VERIFIED" | translate}}</span></div>',
            menuItems: [{
                title: $translate.instant('NAME_FILTER'),
                icon: 'ui-grid-icon-filter',
                action: function(){
                    openModalFilter($rootScope, $scope, $http, $modal, $cookieStore, gridService, 'name');
                }
            }]
        },
        { field: 'keywords' , name: $translate.instant('KEYWORDS'), width:'15%', minWidth:100,  enableSorting: false, enableHiding: false,
            menuItems: [{
                title: $translate.instant('KEYWORD_FILTER'),
                icon: 'ui-grid-icon-filter',
                action: function(){
                    openModalFilter($rootScope, $scope, $http, $modal, $cookieStore, gridService, 'keyword');
                }
            }]
        },
        { field: 'companyDesc' , name: $translate.instant('DESC'), width:'43%', minWidth:300,  enableSorting: false,
            cellTemplate: '<div class="grid-desc ui-grid-cell-contents tool" title="{{row.entity.companyDesc}}">'
            //+'{{row.entity[col.field]}}'
           + '{{row.entity.company.description}}'
            +'</div>'},
        { field: 'stage', name: $translate.instant('STAGE'), width:'11%', minWidth:60,
            cellTemplate: '<div class="grid-desc ui-grid-cell-contents tool" title="{{row.entity.company.round}}">'
             + '<span ng-show="row.entity.company.round == null || row.entity.company.round == 0">N/A</span>'
            + '{{row.entity.company.roundDesc}}'
            +'</div>'
        },
        { field: 'location' , name: $translate.instant('LOC'), width:'11%', minWidth:60, enableHiding: false,
            menuItems: [{
                title: $translate.instant('LOCATION_FILTER'),
                icon: 'ui-grid-icon-filter',
                shown: true
            }]},
        //{ field: 'status', name: $translate.instant('STATUS'), width: '8%', minWidth:80}
        //{ field: 'website', name: $translate.instant('WEBSITE') , minWidth:150,  enableSorting: false,
        //    cellTemplate: '<div class="grid-website ui-grid-cell-contents">'+
        //    '<span ng-show="row.entity.website == null || row.entity.website.length == 0">N/A</span>'+
        //    '<a href="{{row.entity[col.field]}}" target="_blank" ng-show="row.entity.website != null">{{row.entity[col.field]}}</a></div>'}
    ];
    $cookieStore.remove('ls_select_rows');
    $scope.gridOptions = {
        headerRowHeight: 50,
        rowHeight: 40,
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
            url: 'api/search/company',
            headers: {'Content-Type': 'application/json'},
            data:  params,
            responseType: 'json'
        }

        $http(req)
            .success(function(data) {
                $rootScope.total = data.total;
                codeArr = data.companyIds;
                console.log(codeArr);
            })
            .then(function(){
                if(codeArr.length == 0){
                    return;
                }

                var promise = $q.defer();
                var reqDetail = {
                    method: 'POST',
                    //url: './api/company/getCompanies',
                    url: pre_address+'/api/site/company/getCompanies',
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