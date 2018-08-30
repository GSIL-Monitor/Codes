var Reflux = require('reflux');
var $ = require('jquery');
var ColdcallActions = require('../action/ColdcallActions');

var Functions = require('../../../react-kit/util/Functions');
var Http = require('../../../react-kit/util/Http');

const ColdcallStore = Reflux.createStore({
    store: {
        coldcallId: null,
        coldcall: null,
        files: null,
        candidates: null,
        companies: null,
        searchResult: null,
        extend: false,
        collegues: [],
        forwardUser: null,
        forward_steps: []
    },

    init(){
        this.listenToMany(ColdcallActions);
    },

    onInit(coldcallId){
        this.store.coldcallId = Number(coldcallId);
        this.onGetColdCall();
        this.onGetCandidates();
        this.onGetCompanies();
        this.getCollegues();
        this.getForwards();
    },

    onGetColdCall() {
        var payload = {payload: {coldcallId: this.store.coldcallId}};
        var url = "/api/company/coldcall/detail";
        Http.ajax(payload, url, function (result) {
            if (result.code == 0) {
                this.store.coldcall = result.coldcall;
                this.store.files = result.files;
                this.trigger(this.store);
            }
        }.bind(this));
    },

    onGetCandidates() {
        var payload = {payload: {coldcallId: this.store.coldcallId}};
        var url = "/api/company/coldcall/candidates";
        Http.ajax(payload, url, function (result) {
            //console.log(result);
            if (result.code == 0) {
                this.store.candidates = result.candidates;
                this.trigger(this.store);
            }
        }.bind(this));
    },

    onGetCompanies() {
        var payload = {payload: {coldcallId: this.store.coldcallId}};
        var url = "/api/company/coldcall/companies";
        Http.ajax(payload, url, function (result) {
            //console.log(result);
            if (result.code == 0) {
                this.store.companies = result.companies;
                this.trigger(this.store);
            }
        }.bind(this));
    },

    onSelect(code) {
        var payload = {
            payload: {
                coldcallId: this.store.coldcallId,
                code: code
            }
        };
        var url = "/api/company/coldcall/select";
        Http.ajax(payload, url, function (result) {
            if (result.code == 0) {
                ColdcallActions.getCompanies(this.store.coldcallId);
                $('.hint').html('已添加').show().fadeOut(2000);
            }
        }.bind(this));
    },

    onRemove(code) {
        var payload = {payload: {coldcallId: this.store.coldcallId, code: code}};
        var url = "/api/company/coldcall/remove";
        Http.ajax(payload, url, function (result) {
            if (result.code == 0) {
                //ColdcallActions.getCompanies(this.store.coldcallId);
                var matches = this.store.companies;
                for (var i in matches) {
                    if (code == matches[i].code) {
                        matches.splice(i, 1);
                    }
                }
                $('.hint').html('已删除').show().fadeOut(2000);
                this.trigger(this.store);
            }
        }.bind(this));
    },

    onExtend(){
        if (this.store.extend)
            this.store.extend = false;
        else
            this.store.extend = true;
        this.trigger(this.store);
    },

    onDecline(declineId){
        declineId = Number(declineId);
        var payload = {payload: {coldcallId: this.store.coldcallId, declineId: declineId}};
        var url = "/api/company/coldcall/decline";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.coldcall.declineStatus = declineId;
                $('.hint').html('已拒绝').show().fadeOut(2000);
                this.trigger(this.store);
            }
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onSelectForwardUser(value){
        this.store.forwardUser = value;
        this.trigger(this.store);
    },

    onForward(){
        var payload = {payload: {coldcallId: this.store.coldcallId, forwardUser: Number(this.store.forwardUser)}};
        var url = "/api/company/coldcall/forward";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.forwardUser = null;
                $('#select-forward').val(0);
                $('.hint').html('转发成功!已从任务中移除').show().fadeOut(2000);
                $('.modal').hide();
                setTimeout(function(){window.history.back();}, 1000)
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    /**** get ****/
    getCollegues(){
        var payload = {payload: {}};
        var url = "/api/company/coldcall/collegues";
        var callback = function (result) {
            if (result.code == 0) {
                if (result.list != null) {
                    if (result.list.length > 0) {
                        var list = result.list;
                        var select = [];
                        var ele = {value: 0, name: '请选择转发对象'};
                        select.push(ele);

                        for (var i in list) {
                            ele = {};
                            ele.value = list[i].id;
                            ele.name = list[i].username;
                            select.push(ele);
                        }
                        this.store.collegues = select;
                    }
                }
                this.trigger(this.store);
            }
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    /***get forwards**/
        getForwards(){
        var payload = {payload: {coldcallId: this.store.coldcallId}};
        var url = "/api/company/coldcall/getForwards";
        var callback = function (result) {
            if (result.code == 0) {
                if (result.list!=null&&result.list.length > 0) {
                    this.store.forward_steps = result.list;
                    this.trigger(this.store);
                }
            }
        }.bind(this);

        Http.ajax(payload, url, callback);
    }

});

module.exports = ColdcallStore;