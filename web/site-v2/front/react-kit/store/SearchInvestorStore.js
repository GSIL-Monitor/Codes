var Reflux = require('reflux');
var $ = require('jquery');
var InvestorActions = require('../action/SearchInvestorActions');
var Http = require('../util/Http');
var SearchUtil = require('../util/SearchUtil');
var Functions = require('../util/Functions');

var CompanyStore  = require('../../webapp-site/js/store/CompanyStore');

const SearchInvestorStore = Reflux.createStore({
    store:{
        value: null,
        id: null,
        match: null,
        hint: null,
        selected: null,
        from: null
    },

    init() {
        this.listenToMany(InvestorActions);
    },

    onInit(value, from){
        this.store.value = value;
        this.store.from = from;
        this.trigger(this.store);
    },

    onGet(value){
        if(Functions.isNull(value))
            return;

        var params = {data: value, field: 'investor'};
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
            this.store = SearchUtil.doInvestorMatch(this.store);
            if(this.store.from == 'updateInvestor'){
                CompanyStore.store.selectedFIR.investorId = this.store.id;
                CompanyStore.store.selectedFIR.name=this.store.name;
                CompanyStore.trigger(CompanyStore.store);
            }

            this.trigger(this.store);
        }

        if(value ===38 || value === 40){
            result = SearchUtil.getInvestorSelected(value, this.store.selected, this.store.hint);
            this.store.selected = result;
            this.trigger(this.store);
        }

    },

    onClickSearch(value){
        this.store = SearchUtil.doInvestorMatch(this.store);
        if(this.store.from == 'updateInvestor'){
            CompanyStore.store.selectedFIR.investorId = this.store.id;
            CompanyStore.store.selectedFIR.name=this.store.name;
            CompanyStore.trigger(CompanyStore.store);
        }
        this.trigger(this.store);
    }


});



module.exports = SearchInvestorStore;