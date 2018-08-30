/**
 * Created by haiming on 15/12/4.
 */
angular.module('gobi')
    .controller('ListCtrl', ListCtrl)
    .controller('ListDetailCtrl',ListDetailCtrl)
    .controller('ListGridCtrl', ListGridCtrl)


function ListCtrl($scope, $http, listService) {
    $scope.page = 1;

    $http.get(pre_address+'/api/site/user/list/get?page=1').success(function(data){
       $scope.userList = data.userList;
        $scope.companyListVOList=  $scope.userList.companyListVOList;
        //$scope.heartList = data.heartList;
        $scope.listCount = $scope.userList.listCount;
        listService.newData(data.userList);
    })

    $scope.$watch(function(){return listService.getData()}, function (newValue, oldValue) {
        if (newValue === oldValue) return;
        $scope.userList = newValue;
    });

}


function ListDetailCtrl($rootScope, $scope, $http, $modal, $location, $cookieStore, listGridService, $translate, $stateParams){

    var id = $stateParams.id;
    //todo url
    $http.get(pre_address+'/api/site/user/list/overview?id='+id).success(function(data){
        $scope.listInfo = data.listInfo;
        $scope.companyList = data.companyList;
        $rootScope.total = data.companyList.length;
        listGridService.newData($scope.companyList);

        setPageTitle($scope.listInfo.name)

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


function ListGridCtrl($rootScope, $scope, $interval, $q, $cookieStore, $translate, listGridService) {

    $scope.colDefs = [
        { field: 'productName', name: $translate.instant('NAME'), width:'18%', minWidth:100,  enableSorting: false, enableHiding: false,
            cellTemplate: '<div class="grid-name ui-grid-cell-contents"><a href="#/company/{{row.entity.company.code}}/overview">{{row.entity.company.name}}</a>' +
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
        { field: 'companyDesc' , name: $translate.instant('DESC'), width:'37%', minWidth:300,  enableSorting: false,
            cellTemplate: '<div class="grid-desc ui-grid-cell-contents tool" title="{{row.entity.company.description}}">'
            //+'{{row.entity[col.field]}}'
            + '{{row.entity.company.description}}'
            +'</div>'},
        { field: 'establishDate' , name: $translate.instant('FOUNDED'), width:'10%', minWidth:100,
            cellTemplate:'<div class="grid-name ui-grid-cell-contents">'+
            '<span ng-hide="row.entity.company.establishDate != null">N/A</span>'+
            '<span ng-show="row.entity.company.establishDate != null">{{row.entity.company.establishDate.slice(0,7)}}</span>'+
            '</div>'
        },
        { field: 'stage', name: $translate.instant('STAGE'), width:'10%', minWidth:100,
            cellTemplate: '<div class="ui-grid-cell-contents">'
            + '<span ng-show="row.entity.company.roundDesc!= null">{{row.entity.company.roundDesc}}'+
            '</div>'
        },
        { field: 'location' , name: $translate.instant('LOC'), width:'10%', minWidth:100, enableHiding: false},
        //{ field: 'status', name: $translate.instant('STATUS'), width: '6%', minWidth:60}
        //{ field: 'website', name: $translate.instant('WEBSITE') , minWidth:150,  enableSorting: false,
        //    cellTemplate: '<div class="grid-website ui-grid-cell-contents">'+
        //    '<span ng-show="row.entity.website == null || row.entity.website.length == 0">N/A</span>'+
        //    '<a href="{{row.entity[col.field]}}" target="_blank" ng-show="row.entity.website != null">{{row.entity[col.field]}}</a></div>'}
    ];


    $cookieStore.remove('ls_select_rows')
    gridBasic($rootScope, $scope, $interval, $q, $cookieStore, 'ls_select_rows', listGridService)

}