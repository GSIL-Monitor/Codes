var Reflux = require('reflux');
var $ = require('jquery');
var DemoDayActions = require('../action/DemoDayActions');
var Functions = require('../../../react-kit/util/Functions');
var DemodayUtil = require('../util/DemodayUtil');
var ValidateStore = require('./validation/ValidateDemodayStore');
var Http = require('../../../react-kit/util/Http');

const DemoDayStore = Reflux.createStore({
    store: {
        //新增是的demoday
        demoday: DemodayUtil.createBlankDemoday(),
        demodayId: null,
        oldDemoday: null,
        //更新操作的demoday
        newDemoday: null,
        // 缓存demoday 的date
        strDates:[],
        updateDemoday: false,
        orgList: null,
        addOrgIds: [],
        joinOrgs: null,
        rejectOrgs: null,
        //demodayCompany
        demodayCompanies: null,
        //是否更新company
        updateCompany: false,
        //公司平均分和partner打分
        preScores: null,
        //所有用户打分
        userScores: null,
        //preScore批量操作
        batchOperate: false,
        selectedIds: [],
        sysCompanyList:[],
        sysCompanyBatch:false,
        selectedAll:false
    },

    init: function () {
        this.listenToMany(DemoDayActions);
    },

    onGetInitData(demodayId){
        this.store.demodayId = demodayId;
        this.store.updateDemoday=false;
        this.trigger(this.store);
        this.getDemoday(demodayId);
        this.getDemodayOrgs(demodayId);
        this.getDemodayCompanies(demodayId);
    },

    onUpdate(value){

        if (value == "demoday") {
            if (this.store.updateDemoday) {
                this.store.newDemoday = Functions.clone(this.store.oldDemoday);
                this.store.strDates=DemodayUtil.getDateList(this.store.newDemoday);
            }
            this.store.updateDemoday = !this.store.updateDemoday;
        }
        if (value == "company") {
            this.store.updateCompany = !this.store.updateCompany;
        }

        this.trigger(this.store);
    },

    onChange(name, value, update,date){
        if(update){
            this.store.newDemoday[name]=value;
        }
        if (update&&date) {
            for(var i in this.store.strDates){
                if(this.store.strDates[i].name==name){
                    this.store.strDates[i].nodeDate =value;
                }
            }

        } else {
            this.store.demoday[name] = value;

        }
        this.trigger(this.store);

    },

    onAdd(){
        //名称存在不予创建
        if (!ValidateStore.store.name.validation) {
            $("#orgName").focus();
            return;
        }
        this.store.add = true;
        this.trigger(this.store)
        DemodayUtil.parserDemoday(this.store.demoday);
        console.log(this.store.demoday);
        var payload = {
            payload: {
                demoday: this.store.demoday,
                orgIds: DemodayUtil.getSelectedIds(this.store.addOrgIds)
            }
        };
        var url = "/api/admin/demoday/add";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.demoday = DemodayUtil.createBlankDemoday();
                this.store.addOrgIds = [];
                window.location.href = "/admin/#/demoday";
            }
            else {
                $('.hint').html('新增失败!').show().fadeOut(3000);
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onGetOrgList(){
        var payload = {payload: {status: 31010}};
        var url = "/api/admin/demoday/orgList";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.orgList = result.list;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);

    },

    onSelectOrg(value){
        var addOrgIds = this.store.addOrgIds;
        var id = {id: value, selected: true};
        if (addOrgIds.length == 0) {
            addOrgIds.push(id);
        }
        else {
            var flag = false;
            for (var i in addOrgIds) {
                if (value == addOrgIds[i].id) {
                    flag = true;
                    if (addOrgIds[i].selected) {
                        addOrgIds[i].selected = false;
                    }
                    else {
                        addOrgIds[i].selected = true;
                    }
                }
            }

            if (!flag) addOrgIds.push(id);
        }
        this.trigger(this.store);
    },

    onUpdateDate(value, update){
        if (!ValidateStore.store.holdDate.validation) {
            return;
        }
        var date = value.substring(0, 10);
        var time = value.substring(10, 15);
        var holdDate = new Date(date);

        var preScoreDate = new Date(holdDate);
        var scoreDoneDate = new Date(holdDate);
        preScoreDate.setDate(holdDate.getDate() - 4);
        scoreDoneDate.setDate(holdDate.getDate() - 1);
        if (update) {
            this.store.newDemoday.preScoreDate = DemodayUtil.dateToString(preScoreDate);
            this.store.newDemoday.scoreDoneDate = DemodayUtil.dateToString(scoreDoneDate);
        }
        else {
            this.store.demoday.preScoreDate = DemodayUtil.dateToString(preScoreDate);
            this.store.demoday.scoreDoneDate = DemodayUtil.dateToString(scoreDoneDate);
        }

        this.trigger(this.store);
    },

    getDemoday(demodayId){
        var payload = {payload: {demodayId: demodayId}};
        var url = "/api/admin/demoday/detail";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.oldDemoday = result.demoday;
                this.store.newDemoday = Functions.clone(this.store.oldDemoday);
                this.store.strDates=DemodayUtil.getDateList(this.store.newDemoday)
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    getDemodayOrgs(demodayId){
        var payload = {payload: {demodayId: demodayId}};
        var url = "/api/admin/demoday/org/list";
        var callback = function (result) {
            if (result.code == 0) {
                var demodayOrgs = DemodayUtil.parseDemodayOrgs(result.list);
                this.store.joinOrgs = demodayOrgs.joinOrgs;
                this.store.rejectOrgs = demodayOrgs.rejectOrgs;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },
    getDemodayCompanies(demodayId){
        var payload = {payload: {demodayId: demodayId}};
        var url = "/api/admin/demoday/company/list";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.demodayCompanies = result.list;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onGetPreScores(demodayId){
        this.getDemoday(demodayId);
        var payload = {payload: {demodayId: demodayId}};
        var url = "/api/admin/demoday/company/avgScores";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.preScores = result.list;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onUpdateDemoday(){
        var strDates = this.store.strDates;

        for(var k in strDates){
            var name= strDates[k].name;
             var strDate = strDates[k].nodeDate;
            var date = new Date(strDate);

            this.store.newDemoday[name]=date.getTime();
        }
        var change = DemodayUtil.compare(this.store.newDemoday, this.store.oldDemoday);
        if (!change) {
            $('.hint').html('请先修改再更新!').show().fadeOut(3000);
            return;
        }
        var payload = {payload: {demoday: this.store.newDemoday}};
        var url = "/api/admin/demoday/update";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.oldDemoday = Functions.clone(this.store.newDemoday);
                this.store.updateDemoday = false;
                this.getDemodayCompanies(this.store.demodayId);
                $('.hint').html('更新成功!').show().fadeOut(3000);
            }
            else {
                $('.hint').html('更新失败!').show().fadeOut(3000);
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onRemoveDemodayOrg(orgId){

        var payload = {payload: {orgId: orgId, demodayId: this.store.demodayId}};
        var url = "/api/admin/demoday/org/reject";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.joinOrgs = DemodayUtil.removeDemodayOrg(this.store.joinOrgs, orgId, this.store.rejectOrgs);
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onAddDemodayOrgs(){
        var orgIds = DemodayUtil.getSelectedIds(this.store.addOrgIds);
        var payload = {
            payload: {
                demodayId: this.store.demodayId,
                orgIds: orgIds
            }
        };
        var url = "/api/admin/demoday/org/join";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.rejectOrgs = DemodayUtil.addDemodayOrgs(this.store.joinOrgs, orgIds, this.store.rejectOrgs);
                this.store.addOrgIds = [];
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onAllPreScores(dealDemodayId){
        var payload = {
            payload: {
                dealDemodayId: dealDemodayId
            }
        };
        var url = "/api/admin/demoday/company/allScores";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.userScores = result.list;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onBatchOperateChange(){
        this.store.batchOperate = !this.store.batchOperate;
        this.store.selectedIds=[];
        this.trigger(this.store);
    },

    onPreScoreResult(demodayCompanyId, scoringStatus){
        var payload = {
            payload: {
                demodayCompanyId: demodayCompanyId,
                scoringStatus: scoringStatus
            }
        };
        var url = "/api/admin/demoday/company/scoringStatus";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.preScores = DemodayUtil.setPreScoreResult(this.store.preScores, demodayCompanyId, scoringStatus);
                $('.hint').html('操作成功').show().fadeOut(3000);
            }
            else {
                $('.hint').html('操作失败').show().fadeOut(3000);
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onSelectedIds(value){
        var addIds = this.store.selectedIds;
        var id = {id: value, selected: true};
        if (addIds.length == 0) {
            addIds.push(id);
        }
        else {
            var flag = false;
            for (var i in addIds) {
                if (value == addIds[i].id) {
                    flag = true;
                    if (addIds[i].selected) {
                        addIds[i].selected = false;
                    }
                    else {
                        addIds[i].selected = true;
                    }
                }
            }
            if (!flag) addIds.push(id);
        }
        this.trigger(this.store);
    },

    onBatchOperate(scoringStatus){
        var ids = DemodayUtil.getSelectedIds(this.store.selectedIds);
        if (ids == null || ids.length == 0) {
            $('.hint').html('请先选中项目!').show().fadeOut(3000);
            return;
        }
        var payload = {
            payload: {
                ids: ids,
                scoringStatus: scoringStatus
            }
        };
        var url = "/api/admin/demoday/company/batchStatus";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.preScores = DemodayUtil.setPreScoreResults(this.store.preScores, ids, scoringStatus);
                this.store.batchOperate = false;
                this.store.selectedIds = [];
                $('.hint').html('操作成功').show().fadeOut(3000);
            }
            else {
                $('.hint').html('操作失败').show().fadeOut(3000);
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onRemoveDemodayCompany(id){
        var payload = {payload: {id:id}};
        var url = "/api/admin/demoday/company/remove";
        var callback = function (result) {
            if (result.code == 0) {
                this.getDemodayCompanies(this.store.demodayId);
                $('.hint').html('操作成功').show().fadeOut(3000);
            }
            else {
                $('.hint').html('操作失败').show().fadeOut(3000);
            }
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onBatchJoinOrNot(joinStatus){
        var ids = DemodayUtil.getSelectedIds(this.store.selectedIds);
        if (ids == null || ids.length == 0) {
            $('.hint').html('请先选中项目!').show().fadeOut(3000);
            return;
        }
        var payload = {
            payload: {
                ids: ids,
                joinStatus: joinStatus
            }
        };
        var url = "/api/admin/demoday/company/batchJoinStatus";
        var callback = function (result) {
            if (result.code == 0) {
                this.getDemodayCompanies(this.store.demodayId);
                this.store.updateCompany = false;
                this.store.selectedIds = [];
                $('.hint').html('操作成功').show().fadeOut(3000);
            }
            else {
                $('.hint').html('操作失败').show().fadeOut(3000);
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onGetSysCompanies(demodayId){
        this.getDemoday(demodayId);
        var payload = {
            payload: {
                demodayId: demodayId,
                orgName: "烯牛快跑",
                start:0,
                pageSize:20
            }
        };
        var url = "/api/admin/demoday/company/sysList";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.sysCompanyList=result.list;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onSysCompanyBatch(){
        this.store.sysCompanyBatch = !this.store.sysCompanyBatch;
        this.store.selectedIds=[];
        this.store.selectedAll=false;
        this.trigger(this.store);
    },
    onSelectSysCompAll(){
        if(this.store.selectedAll){
            this.store.selectedIds=[];
            this.store.selectedAll=false;
        }else{
            var list= this.store.sysCompanyList;
            for(var i in list){
                var id = {id: list[i].id, selected: true};
                this.store.selectedIds.push(id);
            }
            this.store.selectedAll=true;
        }
        this.trigger(this.store);
    },
    onSysCompanyBatchOperate(str,id){
        var ids = DemodayUtil.getSelectedIds(this.store.selectedIds);
        if (ids == null || ids.length == 0) {
            $('.hint').html('请先选中项目!').show().fadeOut(3000);
            return;
        }
        var payload = {
            payload: {
                ids: ids
            }
        };
        var url = "/api/admin/demoday/company/";
        if(str=='Y') url+="pass";
        else url+="notPass";
        var callback = function (result) {
            if (result.code == 0) {
               this.onGetSysCompanies(id);
                this.store.sysCompanyBatch=false;
                this.store.selectedIds=[];
                this.store.selectedAll=false;
                $('.hint').html('操作成功').show().fadeOut(3000);
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    }

});

module.exports = DemoDayStore;