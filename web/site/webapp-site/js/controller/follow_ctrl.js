/**
 * Created by haiming on 15/12/4.
 */
angular.module('gobi')
    .controller('FollowCtrl', FollowCtrl)
    .controller('FollowGridCtrl', FollowGridCtrl)

function FollowCtrl($rootScope, $scope, $http, $modal, $cookieStore, listGridService, $translate){

    url = pre_address+'/api/site/common/followStatus' ;
    $http.get(url).success(function(data){
        $scope.followStatus = data.followStatus;
    })

    $http.get(pre_address+'/api/site/user/company/getByStatus?status=0').success(function(data){
        //$http.get('./api/user/company/getByStatus?status=0').success(function(data){
        $scope.companyList = data.companyList;
        for(var i= 0,leng=$scope.companyList.length;i<leng;i++){
            $scope.companyList[i].followStatus=parseFollowStatus( $scope.companyList[i].followStatus);
        }
        $rootScope.total = data.companyList.length;
        listGridService.newData($scope.companyList);
    })


    $scope.getFollowByStatus = function(status){

        $http.get(pre_address+'/api/site/user/company/getByStatus?status='+status).success(function(data){
        //$http.get('./api/user/company/getByStatus?status='+status).success(function(data){
            $scope.companyList = data.companyList;
            for(var i= 0,leng=$scope.companyList.length;i<leng;i++){
                $scope.companyList[i].followStatus=parseFollowStatus( $scope.companyList[i].followStatus);
            }
            $rootScope.total = data.companyList.length;
            listGridService.newData($scope.companyList);
        })

    }


    $scope.deleteSelected = function(){
        var modalInstance = comfirm($modal);
        modalInstance.result.then(function (callBack) {
            if(callBack.comfirm){
                var codes = $cookieStore.get('ls_select_rows');
                var req = {
                    method: 'delete',
                    url: pre_address+'/api/site/user/company/unfollow',
                    params: {companyCodes : codes}
                }

                $http(req).success(function(data){
                    $http.get(pre_address+'/api/user/company/getByStatus?status=0').success(function(data){
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


function FollowGridCtrl($rootScope, $scope, $interval, $q, $cookieStore, $translate, listGridService) {


    $scope.colDefs = [
        { field: 'name', name: $translate.instant('NAME'), width:'16%', minWidth:100,  enableSorting: false, enableHiding: false,
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
        { field: 'companyDesc' , name: $translate.instant('DESC'), width:'30%', minWidth:300,  enableSorting: false,
            cellTemplate: '<div class="grid-desc ui-grid-cell-contents tool" title="{{row.entity.company.description}}">'
            //+'{{row.entity[col.field]}}'
           + '{{row.entity.company.description}}'
            +'</div>'},
        { field: 'establishDate' , name: $translate.instant('FOUNDED'), width:'6%', minWidth:100,
            cellTemplate:'<div class="grid-name ui-grid-cell-contents">'+
            '<span ng-hide="row.entity.company.establishDate != null">N/A</span>'+
            '<span ng-show="row.entity.company.establishDate != null">{{row.entity.company.establishDate.slice(0,7)}} </span>'+
            '</div>'
        },

        { field: 'stage', name: $translate.instant('STAGE'), width:'6%', minWidth:60,
            cellTemplate: '<div class="ui-grid-cell-contents">'
            + '<span ng-show="row.entity.company.roundDesc!= null">{{row.entity.company.roundDesc}}'+
            '</div>'

        },

        { field: 'location' , name: $translate.instant('LOC'), width:'6%', minWidth:60, enableHiding: false},
        { field: 'followStatus', name: $translate.instant('FOLLOWSTATUS'), width: '10%', minWidth:110

            //cellTemplate: '<div class="ui-grid-cell-contents">'
            //+ '<span ng-show="row.entity.followStatus != null">{{row.entity.followStatus}}'+
            //'</div>'

        },
        { field: 'followStart', name: $translate.instant('FOLLOWSTART') , minWidth:150,
            cellTemplate: '<div class="ui-grid-cell-contents">'+
            '<span ng-hide="row.entity.followDate != null">N/A</span>'+
            '<span ng-show="row.entity.followDate != null">{{row.entity.followDate.slice(0,10)}}'+
            '</div>'
        }
    ];

    $cookieStore.remove('ls_select_rows')
    gridBasic($rootScope, $scope, $interval, $q, $cookieStore, 'ls_select_rows', listGridService)

}