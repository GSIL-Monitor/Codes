var Reflux = require('reflux');
var $ = require('jquery');
var CompanyActions = require('../action/SearchCompanyActions');
var Http = require('../util/Http');
var SearchUtil = require('../util/SearchUtil');
var Functions = require('../util/Functions');

var CompsStore = require('../../webapp-site/js/store/company/CompsStore');
var ColdcallStore = require('../../webapp-site/js/store/ColdcallStore');
var DemoDayStore = require('../../webapp-site/js/store/demoday/DemoDayStore');

const SearchCompanyStore = Reflux.createStore({
    store:{
        value: null,
        type: null,
        from: null,
        hint: null,
        selected: null,
        list: [],
        matches: [],
        demodayId : null
    },

    init(){
        this.listenToMany(CompanyActions);
    },

    onInit(from, demodayId){
        this.store.from = from;
        this.store.demodayId = demodayId;
        this.trigger(this.store);
        $('.search-company-hint').hide();
    },

    onGet(value){
        if(Functions.isNull(value))
            return;

        var params = {data: value, field: 'name'};
        var url = '/api/search/complete';
        var callback =  function(result) {
            this.store.hint = result;
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(params, url, callback);
    },

    onChange(value){
        this.store.selected = null;
        this.store.value = value;

        this.onGet(value);
        this.trigger(this.store);
    },

    onSelect(value){
        this.store.selected = value;
        this.trigger(this.store);
    },

    onUnselect(){
        this.store.selected = null;
        this.trigger(this.store);
    },


    onKeydown(value){
        var result;
        if(value === 13){
           this.onClickSearch(value);
        }

        if(value ===38 || value === 40){
            result = SearchUtil.getCompanySelected(value, this.store.selected, this.store.hint);
            this.store.selected = result;
            this.trigger(this.store);
        }

    },

    onClickSearch(){
        if(Functions.isNull(this.store.value)) return;

        if(this.store.from == 'coldcall'){
            this.coldcallSearch();
            return;
        }

        if(this.store.from == 'demoday'){
            this.demodaySearch();
            return;
        }

        if(this.store.selected == null) return;
        this.store = SearchUtil.doCompanyMatch(this.store);

        if(this.store.from == 'comps'){
            var list = this.store.matches;
            if(list.length == 0 )return;
            this.store.matches = [];

            var payload = {payload: {code: list[0].code}};
            var url = "/api/company/comps/get";
            var callback = function (result) {
                if (result.code == 0) {
                    CompsStore.store.newList = this.addComps(CompsStore.store.newList, result.company)
                }
                CompsStore.trigger(CompsStore.store);
            }.bind(this);

            Http.ajax(payload, url, callback);
        }

        this.trigger(this.store);
    },

    onDelete(code){
        var list = this.store.matches;
        for(var i in list){
            if(code == list[i].code){
                list.splice(i, 1);
            }
        }
        this.trigger(this.store);
    },


    addComps(list, value){
        var flag = false;
        for(var i in list){
            if(value.code == list[i].company.code ){
                flag = true;
            }
        }
        if(!flag) list.push(value);

        console.log(list);
        return list
    },




    /******** search *********/
    coldcallSearch(){
        if(this.store.selected != null){
            //this.store = SearchUtil.doCompanyMatch(this.store);
            ColdcallStore.onSelect(this.store.selected.code);
        }
        else{
            if(!Functions.isEmptyObject(this.store.hint)){
                if(this.store.hint.name.length > 0){
                    var hints = this.store.hint.name;
                    var codes = [];
                    for(var i in hints){
                        codes.push(hints[i].code);
                    }

                    var payload={payload: {codes: codes}};
                    var url = "/api/company/list";
                    var callback = function(result){
                        if(result.code == 0) {
                            if(result.list == null) result.list = [];
                            this.store.list = result.list;

                        }
                        else{
                        }
                        this.trigger(this.store);
                    }.bind(this);

                    Http.ajax(payload, url, callback);

                    ColdcallStore.store.extend = true;
                }else{
                    ColdcallStore.store.extend = false;
                }

            }else{
                this.store.list = [];
                ColdcallStore.store.extend = false;
            }

            ColdcallStore.store.searchResult = true;
            ColdcallStore.trigger(ColdcallStore.store);


        }
        ColdcallStore.trigger(ColdcallStore.store);
        $('.search-company-hint').hide();
    },

    demodaySearch(){
        if(this.store.selected != null){
            //DemoDayStore.onAddCompany(this.store.selected);
            window.location.href = '/#/demoday/'+this.store.demodayId+'/add/'+this.store.selected.code;
        }else{
            if(!Functions.isEmptyObject(this.store.hint)){
                if(this.store.hint.name.length > 0){
                    var hints = this.store.hint.name;
                    var codes = [];
                    for(var i in hints){
                        codes.push(hints[i].code);
                    }

                    var payload={payload: {codes: codes}};
                    var url = "/api/company/list";
                    var callback = function(result){
                        if(result.code == 0) {
                            if(result.list == null) result.list = [];
                            this.store.list = result.list;
                        }
                        else{
                        }
                        this.trigger(this.store);
                    }.bind(this);

                    Http.ajax(payload, url, callback);

                    DemoDayStore.store.extend = true;
                }else{
                    DemoDayStore.store.extend = false;
                }

            }else{
                this.store.list = [];
                DemoDayStore.store.extend = false;
            }

            DemoDayStore.store.searchResult = true;
            DemoDayStore.trigger(DemoDayStore.store);
        }
        DemoDayStore.trigger(DemoDayStore.store);
        $('.search-company-hint').hide();
    },



});



module.exports = SearchCompanyStore;