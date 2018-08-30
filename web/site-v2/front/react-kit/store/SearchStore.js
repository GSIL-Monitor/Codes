var Reflux = require('reflux');
var $ = require('jquery');
var SearchActions = require('../action/SearchActions');
var Http = require('../util/Http');
var SearchUtil = require('../util/SearchUtil');
var Functions = require('../util/Functions');

var HeaderActions = require('../action/HeaderActions');

const SearchStore = Reflux.createStore({
    store:{
        list: null,
        search: null,
        type: null,
        hint: null,
        selected: null
    },

    init() {
        this.listenToMany(SearchActions);
    },

    onInit(type, value){
        this.clean();
        this.store.type = type;
        this.store.search = value;
        this.trigger(this.store);
    },

    onInitMobile(value){
        this.clean();
        this.store.search = value;
        this.trigger(this.store);
    },

    onGet(value){
        this.store.search = value;
        var params = {data: value};
        var url = '/api/search/complete';
        var callback =  function(result) {
            this.store.hint = result;
            $('.search-hint').show();
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(params, url, callback);
    },

    onChange(value){
        this.store.selected = null;
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
            this.onClickSearch();
        }

        if(value ===38 || value === 40){
            $('.search-hint').show();
            result = SearchUtil.getSelected(value, this.store.selected, this.store.hint);
            this.store.selected = result;
            this.trigger(this.store);
        }

    },

    onClickSearch(){
        var url = SearchUtil.doSearch(this.store.type, this.store.search, this.store.selected);
        this.store.selected = null;
        window.location.href = url;
    },

    clean(){
        this.store = {
            list: null,
            search: null,
            type: null,
            hint: null,
            selected: null
        };
        this.trigger(this.store);
    }


});



module.exports = SearchStore;