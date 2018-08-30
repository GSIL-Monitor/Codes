/**
 * Created by haiming on 15/11/30.
 */
angular.module('gobi')
    .controller('CompanyOverviewCtrl', CompanyOverviewCtrl)
    .controller('CompanyTeamCtrl', CompanyTeamCtrl)
    .controller('CompanyHeadCtrl', CompanyHeadCtrl)
    .controller('MemberDetailCtrl', MemberDetailCtrl)

pre_address = 'http://localhost/web-site';
function CompanyOverviewCtrl($scope, $http, $location, $translate, $stateParams){

      var code = $stateParams.companyCode;

    var url = pre_address+'/api/site/company/overview?code='+code;
    $http.get(url).success(function(data){

        //companyVO
        $scope.company = data.company;
        $scope.subCompany=$scope.company.company;

        var today = new Date();
        var dd = today.getDate();
        var mm = today.getMonth()+1; //January is 0!

        var yyyy = today.getFullYear();
        if(dd<10){
            dd='0'+dd
        }
        if(mm<10){
            mm='0'+mm
        }
        var today = mm+'/'+dd+'/'+yyyy;

        if($scope.company.userCompanyFollow == null){
            $scope.status = 1401;
            $scope.start = today;

        }
        else {
            $scope.status = $scope.company.userCompanyFollow.status;
            var start = $scope.company.userCompanyFollow.followDate;
            if(start != null){
                var	date = new Date(start);
                today = (date.getMonth()+1)+'/'+date.getDate()+"/"+date.getFullYear();
            }
            $scope.start = today;
        }

        var text;
        $http.get(pre_address+'/api/site/common/followStatus').success(function(data){

            angular.forEach(data.followStatus, function(value, key){
                if($scope.status == value.id)
                    text = value.text;
            })

            var option = "<option value='"+$scope.status+"' selected='selected'>"+text+"</option>";
            $("#select").append(option);

            $('select').select2({
                minimumResultsForSearch: Infinity,
                theme: "classic",
                data:data.followStatus
            });



        }).then(function(){

            //$('#select').find("option[value="+$scope.status+"]").attr("selected",true);
        })

        //get description from service
        $scope.descAll = $scope.subCompany.description.split(/\r?\n/);

        var count = 0;
        var desc = [];
        var flag = false;
        angular.forEach($scope.descAll, function(value, key){

            if( !flag && count < 400 && desc.length < 6){
                count += value.length;
                if(value != "")
                    desc.push(value);
            }
            else
                flag = true;

            $scope.desc = desc;
            $scope.descMore = flag;
        })

        $scope.footprintList = data.company.footprintList.reverse();
        $scope.domainList = data.company.domainList;
        $scope.sourceCompanyList=data.company.sourceCompanyList;//todo
        $scope.fundingList=data.company.fundingList;
        for(var i= 0,leng=$scope.fundingList.length;i<leng;i++)
        {
            $scope.fundingList[i].investment=parseMoney($scope.fundingList[i].investment.toString());
        }

        var list = [];
        angular.forEach($scope.company.artifactList, function (artifact)
            {
               var lk= artifact.link;
                if(lk.substring(0,4)!='http'&&lk.substring(0,4)!='wwww.')
                {
                    lk= 'www.'+lk+'.com';
                }
                list.push(lk);
            });
        $scope.linkList =list;

        $scope.sourceCompanyList=data.company.sourceCompanyList;
        $scope.sourceList=new Array();
        //var sourceContext={sourceUrl:null,sourceName:null}
        for(var k= 0, lg=$scope.sourceCompanyList.length;k<lg;k++) {


            var sourceInfo = parseComSource($scope.sourceCompanyList[k].source,$scope.sourceCompanyList[k].sourceId)
            $scope.sourceList.push(sourceInfo);

        }
        //解析产品种类
        $scope.atTypeList=[];
       angular.forEach(data.artifactType,function(type){
        var typeName = parseArtifactType(type);
           $scope.atTypeList.push(typeName);
       });

        $http.get(pre_address+'/api/site/company/artifact?id='+$scope.subCompany.id+'&type=All').success(function(data){
            $scope.currentItem='All';
            $scope.artifact = data.artifact;
        })
        $scope.getArtifactByType =function(type){
            $http.get(pre_address+'/api/site/company/artifact?id='+$scope.subCompany.id+'&type='+type).success(function(data){
                $scope.artifact = data.artifact;
                $scope.currentItem = type;
            })
        }




    }).error(function(){
        $location.path('/');
    }).then(function(){

        //$http.get('./api/company/lagou/info?code='+code).success(function(data){
        //    if(data.lagouInfo == null)
        //        return;
        //    var lagouInfo = data.lagouInfo;
        //    $scope.headCount = lagouInfo.headCountName;
        //})


        //$http.get('./api/user/list/getFeature?code='+code).success(function(data){
        //    $scope.userList = data.userList;
        //})

        $http.get(pre_address+'/api/site/user/list/getExsiting?code='+code).success(function(data){
            $scope.exsitingList = data.exsitingList;
            $scope.companyListVOList = $scope.exsitingList.companyListVOList;
        }).error(function(){
            $location.path('/');
        })

    })

    $scope.more = function(){
        $scope.desc = $scope.descAll;
        $scope.descMore = false;
    }

    $scope.updateFollow = function(){
        var status = $("#select").val()
        var start = $("#follow-date").val()

        if(start == null || start == ""){
            $("#follow-date").focus();
            return;
        }

        if($scope.company.userCompanyFollow != null){
            //console.log($scope.company.userCompanyFollow.heart=='Y')
            if(status == $scope.status && start == $scope.start && $scope.company.userCompanyFollow.active=='Y') return;
        }

        var req = {	method: 'put',
            url: pre_address+'/api/site/user/company/updateFollow',
            params: { code: code, status: status, start: start}
        }
        $http(req).success(function(data){
            $scope.status = status;
            $scope.start = start;
        }).then(function(){
            $('.heart').addClass('fa-heart');
            $('.heart').removeClass('fa-heart-o');
            alertDiv($translate.instant('SAVED'), $translate.instant('UPDATE_FOLLOW_SUCCESS'));
        })


    }

    $scope.saveNote = function (){
        var note = $('#company-note').val();

        if($scope.company.userCompanyNote != null){
            var oldNote = $scope.company.userCompanyNote.note;
            if(note == oldNote) return;
        }else{
            if(note == '' || note == null) return;
        }

        var req = {	method: 'put',
            url: pre_address+'/api/site/user/company/updateNote',
            params: { code: code, note: note}
        }
        $http(req).success(function(data){
            $scope.company.userCompanyNote.note = note;
        }).then(function(){
            $('.heart').addClass('fa-heart');
            $('.heart').removeClass('fa-heart-o');
            alertDiv($translate.instant('SAVED'), $translate.instant('UPDATE_NOTE_SUCCESS'));
        })
    }

}
function CompanyTeamCtrl($scope, $http, $location, $stateParams){

    var code = $stateParams.companyCode;

    var date = new Date();
    $scope.year = date.getFullYear();

    $http.get(pre_address+'/api/site/company/team?code='+code).success(function(data){
        $scope.team = data.team;
        $scope.jobs = data.jobs;
        $scope.recruit = data.recruit;
        for(var i= 0,len=$scope.team.length;i<len;i++)
        {

            var photo = $scope.team[i].member.photo;
            if(photo!=null){
                photo='http://192.168.1.202/file/'+photo;
                $scope.team[i].member.photo=photo;

            }
        }

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
function CompanyHeadCtrl($rootScope, $scope, $http, $location, $translate, $stateParams){
    var location = $location.absUrl();
    var code = $stateParams.companyCode;
    var name = '';
    var headInfo = '';

    $http.get(pre_address+'/api/site/company/head?code='+code).success(function(data){
        $scope.headInfo = data.headInfo;
        headInfo = data.headInfo;
        name = $scope.headInfo.name;

        setPageTitle(name);

        var logo = headInfo.logo;
        if(logo != null){
            angular.element("#company-logo").append("<img src='http://192.168.1.202/file/"+logo+"/logo.jpg'  height='30' style='margin-bottom:8px;'/>");
        }
        if(headInfo.verify =='Y'){
            var span = '<span class="company-verify ">'+$translate.instant('VERIFIED')+'</span>';
            angular.element("#company-verify").append(span)
        }

    }).error(function(){
        $location.path('/');

    }).then(function(){

        $http.get('/api/news/exist?code='+code).success(function(data){
            if(data == 'Y') {
                var li_class = '<li id="li-events"class="li-href" >';
                if (location.indexOf('events') > -1)
                    li_class = '<li id="li-events"class="li-href cate-active" >';

                var li = li_class +
                    '	<a href="#/company/' + headInfo.companyCode + '/events" category-filter>' +
                    '		<span class="fa-stack ft15">' +
                    '		<i class="fa fa-circle-thin fa-stack-2x"></i>' +
                    '		<i class="fa fa-flag fa-stack-1x"></i>' +
                    '		</span>' +
                    $translate.instant('EVENTS') +
                    '	</a>' +
                    '</li>';
                $("#company-head-ul").append(li);
            }
        }).then(function(){
            $http.get('/api/trends/exist?code='+code).success(function(data){
                $scope.trends = data;
                if($scope.trends == 'Y'){
                    var li_class = '<li id="li-trends"class="li-href" >';
                    if(location.indexOf('trends')>-1)
                        li_class =  '<li id="li-trends"class="li-href cate-active" >';

                    var li = li_class+
                        '<a href="#/company/'+headInfo.companyCode+'/trends" category-filter>'+
                        '	<span class="fa-stack ft15"> '+
                        '	<i class="fa fa-circle-thin fa-stack-2x"></i>'+
                        '		<i class="fa fa-bar-chart fa-stack-1x"></i>'+
                        '		</span> '+
                        $translate.instant('TRENDS')+
                        '	</a> '+
                        '	</li>';
                    $("#company-head-ul").append(li);
                }
            })
        })
    })





    $scope.verify = function(){
        var req = {
            method: 'put',
            url: pre_address+'/api/site/company/verify',
            params: { code: code, verify: 'Y'}
        }
        $http(req).success(function(data){

        }).then(function(){
            alertDiv($translate.instant('SAVED'), $translate.instant('COMPANY_VERIFIED_SUCCESS'));
        })
    }



    $scope.$watch(function(){return $location.absUrl()}, function (newValue, oldValue) {
        if (newValue === oldValue) return;
        if(newValue.indexOf('overview') > -1){
            $('#li-overview').addClass('cate-active')
                .siblings().removeClass('cate-active');
        }
        else if(newValue.indexOf('team') > -1){
            $('#li-team').addClass('cate-active')
                .siblings().removeClass('cate-active');
        }
        else if(newValue.indexOf('trends') > -1){
            $('#li-trends').addClass('cate-active')
                .siblings().removeClass('cate-active');
        }
        else if(newValue.indexOf('crowdfunding') > -1){
            $('#li-cf').addClass('cate-active')
                .siblings().removeClass('cate-active');
        }
        else if(newValue.indexOf('events') > -1){
            $('#li-events').addClass('cate-active')
                .siblings().removeClass('cate-active');
        }

        //setPageTitle(name)
    });

}

function MemberDetailCtrl($scope, $http, $location,$stateParams){
    var id = $stateParams.id;
    $http.get(pre_address+'/api/site/company/member?id='+id).success(function(data){
        $scope.member = data.member;
        $scope.experience = data.experience;
        $scope.member.photo='http://192.168.1.202/file/'+ $scope.member.photo;

    }).error(function(){
        $location.path('/');
    })

}