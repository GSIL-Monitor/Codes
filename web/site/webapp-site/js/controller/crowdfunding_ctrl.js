/**
 * Created by haiming on 15/12/6.
 */
angular.module('gobi')
    .controller('CrowdfundingDetailCtrl', CrowdfundingDetailCtrl)
    .controller('CrowdfundingCtrl',CrowdfundingCtrl)
    .controller('CrowdfundingHeadCtrl',CrowdfundingHeadCtrl)
    .controller('CrowdfundingMemberCtrl',CrowdfundingMemberCtrl)

function CrowdfundingDetailCtrl($scope, $http, $stateParams) {

    var id = $stateParams.id;
    url = pre_address+'/api/site/crowdfunding/get?id='+id;
    $http.get(url).success(function(data){
        $scope.cfVO = data.crowdfundingVO;
        $scope.cf = $scope.cfVO.crowdfunding;
        $scope.scf = $scope.cfVO.sourceCrowdfunding;
        var sourceInfo = parseSourceInfo($scope.scf.source, $scope.scf.sourceId);
        $scope.scf.sourceUrl = sourceInfo.sourceUrl;
        $scope.scf.sourceName = sourceInfo.sourceName;

        $scope.scfDocuList=$scope.cfVO.sourceCfDocumentList;
        $scope.scfLeader=$scope.cfVO.sourceCfLeaderList;
        $scope.doucFlage=false;
        $scope.vedioFlage=false;
        for(var i = 0,len=$scope.scfDocuList.length;i<len;i++)
        {
            var docUrl=$scope.scfDocuList[i].link;
            var docType=$scope.scfDocuList[i].type;
            if(docType==9030){
                //for test
                $scope.scfDocuList[i].link='http://192.168.1.202/file/'+docUrl;
                //  $scope.scfDocuList[i].link='/file/'+docUrl;
            }
            if(docType==9010 && docUrl.substring(0,4)=='http') {
                $scope.doucFlage=true;
            }
            if(docType==9020 && docUrl.substring(0,4)=='http') {
                $scope.vedioFlage=true;
            }
        }
        for(i=0,len= $scope.scfLeader.length;i<len;i++)
        {
            function parseInvType(){
                var type=$scope.scfLeader[i].investorType;
                if(type=='10010') {
                    return 'Person';
                }
                else if(type=='10020') {
                    return 'Company';
                }

            };

            $scope.scfLeader[i].investorType=parseInvType();
        }
        var width = $scope.cf.successRaising / $scope.cf.amountRaising *100
        if (width > 100)
            width = 100;
        $('.first-line').css('width',width+'%')

        $scope.cf.successRaising = parseMoney($scope.cf.successRaising.toString())
        $scope.cf.amountRaising = parseMoney($scope.cf.amountRaising.toString())
        for( i= 0,len=$scope.scfLeader.length;i<len;i++) {
            var inves = $scope.scfLeader[i].investment;
            if(null!=inves) {
                $scope.scfLeader[i].investment = parseMoney($scope.scfLeader[i].investment.toString());
            }
            else continue;
        }
    })


}

function CrowdfundingCtrl($scope, $http, $stateParams, crowdfundingService, cfTotalService) {
    $scope.page = 1;



    $http.get(pre_address+'/api/site/common/crowdfundingStatus').success(function(data){
        $scope.cfStatus = data.list;
    })

    $http.get(pre_address+'/api/site/common/crowdfundingSource').success(function(data){
        $scope.cfSource = data.list;
    })

    var cfStatus=$stateParams.cfStatus;
    var cfSource=$stateParams.cfSource;
    statusList = angular.element('#cfStatus').children();
    statusList.each(function(){
                if(cfStatus==$(this).attr("cf-status")) {
                    $(this).addClass('selected-bg').siblings().removeClass('selected-bg');}
        })
    sourceList = angular.element('#cfSource').children();
    sourceList.each(function(){
        if(cfSource==$(this).attr("cf-source")) {
            $(this).addClass('selected-bg').siblings().removeClass('selected-bg');}
    })

    $http.get(pre_address+'/api/site/crowdfunding/getAll?page=1&status='+cfStatus+'&source='+cfSource).success(function(data){

        $scope.cfList = data.cfList;
        for(var i= 0,len= $scope.cfList.length;i<len;i++){
            //解析status
            $scope.cfList[i].status=parseStatus($scope.cfList[i].status);
            // 解析source和sourceId
          var sourceInfo= parseSourceInfo($scope.cfList[i].source, $scope.cfList[i].sourceId);
            $scope.cfList[i].sourceUrl=sourceInfo.sourceUrl;
            $scope.cfList[i].sourceName=sourceInfo.sourceName;
        }
        $scope.total = data.total;

    })
}

function CrowdfundingHeadCtrl($scope, $http, $stateParams){
    var id = $stateParams.id;
    url = pre_address+'/api/site/crowdfunding/head?id='+id;
    var name = '';
    var headInfo = '';
    $http.get(url).success(function(data) {

        $scope.headInfo = data.headInfo;
        console.log($scope.headInfo)
        headInfo = data.headInfo;
        name = $scope.headInfo.name;

    }).error(function() {
        $location.path('/');
    })

}

function CrowdfundingMemberCtrl($scope, $http, $stateParams) {
    var id = $stateParams.id;
    url = pre_address+'/api/site/crowdfunding/member?id='+id;
    $http.get(url).success(function(data) {

        $scope.member=data.member;
        for(var i = 0,len=$scope.member.length;i<len;i++){
            $scope.member[i].photo='http://192.168.1.202/file/'+$scope.member[i].photo;
        }
    console.log( $scope.member);
    }).error(function() {
        $location.path('/');
    })

}