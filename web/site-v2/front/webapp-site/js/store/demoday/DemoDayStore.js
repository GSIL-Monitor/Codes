var Reflux = require('reflux');
var $ = require('jquery');
var DemoDayActions = require('../../action/demoday/DemoDayActions');
var Functions = require('../../../../react-kit/util/Functions');
var Http = require('../../../../react-kit/util/Http');
var DemoDayUtil = require('../../util/DemoDayUtil');

const DemoDayStore = Reflux.createStore({
    store:{
        companies: [],
        noPasses: [],
        companyName:null,
        id: null, //demodayId
        code: null,
        type: null,
        status: null,
        scoringStatus: null,
        orgId: null,
        orgName: null,
        partner: false,

        preScore: 0,
        score: [0, 0, 0, 0, 0],
        ratingPreScore: 0,
        ratingIndustry: 0,
        ratingTeam: 0,
        ratingProduct: 0,
        ratingGain: 0,
        ratingPreMoney: 0,
        decision: null,

        submitScore: false,

        addCompany: null,
        searchResult: false,
        extend: false,

        loadDone: false,
        submitFlag: false,
        update: false,
        recommendation: null,
        demodayCompany: {},
        updateDemodayCompany: {},
        commitOrg: false,

        last: false,
        nextCode: null,
        loading: false,
        firstLoad: false,
        noPassCount: 0
    },

    init(){
        this.listenToMany(DemoDayActions);
    },

    onGetDemoDay(id){
        //this.clean();
        id = Number(id);
        this.store.id = id;
        var payload = {payload: {demodayId: id}};
        var url = "/api/company/demoday/get";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.selectedDemoDay = result.demoday;
                this.store.status = result.demoday.demoday.status;
                var status = result.demoday.demoday.status;
                if(status <= 26020){
                    this.onGetPreScores();
                }else{
                    this.onGetScores();
                }

                this.onGetNOPasses();
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onGetDemoDayNav(id, code){
        var payload = {payload: {demodayId: Number(id), code: code}};
        var url = "/api/company/demoday/nav";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.selectedDemoDay = result.demoday;
                if(result.demoday.demoday != null)
                    this.store.status = result.demoday.demoday.status;
                this.store.companyName = result.companyName;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onGetPreScores(){
        var payload = {payload: {demodayId: this.store.id}};
        var url = "/api/company/demoday/preScore/list";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.companies = result.list;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onGetScores(){
        var payload = {payload: {demodayId: this.store.id}};
        var url = "/api/company/demoday/score/list";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.companies = result.list;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },


    /*** demo day score ***/

    initScore(id, code, type){
        this.store.id = id;
        this.store.code = code;
        this.store.type = type;
        if(type == 'preScore')
            this.onGetPreScore(id, code);
        else{
            this.onGetPreScore(id, code);
            this.onGetScore(id, code);
            this.onGetDecision(id, code);
        }

        this.trigger(this.store);
    },

    onGetPreScore(id, code){
        var payload = {payload: {demodayId: Number(id), code: code}};
        var url = "/api/company/demoday/preScore/get";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.scoringStatus = result.status;
                this.store.preScore = result.preScore;
                this.store.last = result.last;
                this.store.nextCode = result.nextCode;
            }
            this.store.ratingPreScore = 0;
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onGetScore(id, code){
        var payload = {payload: {demodayId: Number(id), code: code}};
        var url = "/api/company/demoday/score/get";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.scoringStatus = result.status;
                this.store.partner = result.partner;
                this.store.orgId = result.orgId;

                var score = result.score;
                if(score == null){
                    this.store.score = [0, 0, 0, 0, 0];
                }else{
                    var scores = [];
                    scores.push(score.industry);
                    scores.push(score.team);
                    scores.push(score.product);
                    scores.push(score.gain);
                    scores.push(score.preMoney);
                    this.store.score = scores;
                }

                this.store.ratingGain = 0;
                this.store.ratingIndustry = 0;
                this.store.ratingPreMoney = 0;
                this.store.ratingProduct = 0;
                this.store.ratingTeam = 0;
                this.store.submitScore = false;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onGetDecision(id, code){
        var payload = {payload: {demodayId: Number(id), code: code}};
        var url = "/api/company/demoday/result/list";
        var callback = function (result) {
            if (result.code == 0) {
                if(result == null) return;
                this.store.decision = result.result;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onRating(score, type){
        this.store = DemoDayUtil.rating(this.store, score, type);
        if(type == 'preScore'){
            this.submitPreScore(score);
        }
        this.trigger(this.store);
    },

    onSubmitScore(){
        var scores = DemoDayUtil.getScores(this.store);

        var payload = {payload: {demodayId: Number(this.store.id),
                                code: this.store.code,
                                scores: scores }};
        var url = "/api/company/demoday/score/score";
        var callback = function (result) {
            if (result.code == 0) {
                $('.hint').html('已更新评分').show().fadeOut(2000);
                this.store.submitScore = false;
                this.onGetDecision(this.store.id, this.store.code);
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onDecide(invest){
        var payload = {payload: {demodayId: Number(this.store.id),
                                    code: this.store.code,
                                    result: invest }};
        var url = "/api/company/demoday/result/invest";
        var callback = function (result) {
            if (result.code == 0) {
                var results = this.store.decision.orgResults;
                for(var i in results){
                    if(results[i].orgId == this.store.orgId){
                        results[i].result = invest;
                    }
                }
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onAddCompany(data){
        this.store.addCompany = data;
        console.log(data);
        this.trigger(this.store);
    },


    submitPreScore(score){
        var payload = {payload: {demodayId: Number(this.store.id),
                                 code: this.store.code,
                                 score: score }};
        var url = "/api/company/demoday/preScore/score";
        var callback = function (result) {
            if (result.code == 0) {
                if(!Functions.isNull(this.store.nextCode)){
                    $('.hint').html('已更新评分，跳转下一个~').show().fadeOut(2000);
                    window.location.href = './#/demoday/'+this.store.id+ '/company/'+this.store.nextCode+'/prescore';
                }
                if(Functions.isNull(this.store.nextCode) && this.store.last)
                    $('.hint').html('已完成全部初筛打分~').show().fadeOut(2000);
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    addDemodayCompany(demodayId, companyId){
        var demodayCompany = {  demodayId: Number(demodayId),
                                companyId: Number(companyId),
                                recommendation: this.store.recommendation
                                };

        var payload = {payload: {demodayCompny: demodayCompany }};
        var url = "/api/company/demoday/company/commit";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.submitFlag = true;
                $('.hint').html('已添加到Demo Day').show().fadeOut(2000);
                window.location.href= '/#/demoday/'+demodayId;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onChangeRecommendation(value){
        this.store.recommendation = value;
        this.trigger(this.store);
    },

    onChangeDemoDayCompany(value){
        this.store.updateDemodayCompany.recommendation = value;
        this.trigger(this.store);
    },


    onUpdate(){
        if(this.store.update)
            this.store.update = false;
        else
            this.store.update = true;

        this.trigger(this.store);
    },

    onComfirm(){
        var payload = {payload: {demodayCompany: this.store.updateDemodayCompany }};
        var url = "/api/company/demoday/company/update";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.update =false;
                this.store.demodayCompany = Functions.clone(this.store.updateDemodayCompany);
                $('.hint').html('已更新推荐理由').show().fadeOut(2000);
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },


    getDemodayCompany(demodayId, companyId){
        var payload = {payload: {demodayId: Number(demodayId), companyId: Number(companyId) }};
        var url = "/api/company/demoday/company/get";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.demodayCompany = result.demodayCompany;
                this.store.updateDemodayCompany = Functions.clone(result.demodayCompany);
                this.store.commitOrg = result.commitOrg;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onGetNOPasses(){
        if(this.store.loading) return;
        if(this.store.firstLoad){
            if(this.store.noPasses.length >= this.store.noPassCount) return;
        }
        this.store.loading = true;
        var payload = {payload: {demodayId: this.store.id, start:this.store.noPasses.length }};
        var url = "/api/company/demoday/notPassedList";
        var callback = function (result) {
            this.store.loading = false;
            if (result.code == 0) {
                this.store.noPasses = this.store.noPasses.concat(result.list);
                this.store.noPassCount = result.total;
                this.store.firstLoad = true;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);

    }

});

module.exports = DemoDayStore;