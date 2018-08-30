var Reflux = require('reflux');
var $ = require('jquery');
var SearchActions = require('../action/SearchActions');
var Functions = require('../../../react-kit/util/Functions');
var SearchUtil = require('../util/SearchUtil');
var Http = require('../../../react-kit/util/Http');


const SearchStore = Reflux.createStore({
    store:{
        search:null,
        open: null,
        type: null,
        names:[],
        keywords: [],
        sectors:[],

        list: [],
        count: null,
        sort: 1,
        filterSectors:[],
        filterRounds:[],
        filterLocations:[],
        filterDates:[],

        loading: false,
        firstLoad: false,
        filterLoad: false

    },

    init() {
        this.listenToMany(SearchActions);
    },

    onSearch(type, value){
        this.clean();
        Functions.updateTitle('search', value);
        this.getSectors();

        if(type == 'latest'){
            this.store.type = type;
            this.onLoadMore();
            return;
        }
        if(Functions.isNull(value)){
            value = '';
        }
        this.store.search = value;
        this.store.type = type;

        this.onLoadMore();
    },

    onGet(data){
        var payload={payload: {codes: data}};
        var url = "/api/company/list";
        var callback = function(result){
            if(result.code == 0) {
                this.store.list = this.store.list.concat(result.list);
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },


    onChangeSearch(value) {
        this.store.search = value;
        this.trigger(this.store);
    },

    onChangeSort(value){
        if(value == this.store.sort)
            return;
        this.store.sort = value;
        this.store.list = [];
        this.onLoadMore();
    },

    onLoadMore(){
        if(this.store.loading) return;
        if(this.store.firstLoad) {
            if (this.store.count == this.store.list.length) {
                return;
            }
        }
        this.store.loading = true;
        this.trigger(this.store);

        var info = SearchUtil.getSearchInfo(this.store);
        var callback = function(result) {
            this.searchCallback(result)
        }.bind(this);

        return Http.ajax(info.params, info.url, callback);
    },

    loadFilter(){
        if(!this.store.filterLoad) return;
        this.store.loading = true;
        this.trigger(this.store);
        var info = SearchUtil.getSearchInfo(this.store);
        var callback = function(result) {
            this.searchCallback(result)
        }.bind(this);

        return Http.ajax(info.params, info.url, callback);
    },


    searchCallback(result){
        this.store.firstLoad = true;
        this.store.loading = false;
        this.store.filterLoad = false;
        this.store.count = result.company.count;
        if(this.store.count > 0){
            this.onGet(result.company.data);
        }else{
            this.trigger(this.store);
        }
    },


    /******************  filter *******************/
    getSectors(){
        var payload = {payload: {}};
        var url = "/api/company/sector/list";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.sectors = result.sectors;
                this.trigger(this.store);
            }
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onFilterSector(value, from){
        var old_store = Functions.clone(this.store);
        this.store.filterSectors = SearchUtil.listChange(value, this.store.filterSectors);
        if(from == 'mobile'){
            this.trigger(this.store);
            return;
        }
        this.filterSearch(old_store);
    },

    onFilterRound(value, from){
        var old_store = Functions.clone(this.store);
        this.store.filterRounds = SearchUtil.listChange(value, this.store.filterRounds);
        if(from == 'mobile'){
            this.trigger(this.store);
            return;
        }
        this.filterSearch(old_store);
    },

    onFilterLocation(value, from){
        var old_store = Functions.clone(this.store);
        this.store.filterLocations = SearchUtil.listChange(value, this.store.filterLocations);
        if(from == 'mobile'){
            this.trigger(this.store);
            return;
        }
        this.filterSearch(old_store);
    },

    onFilterDate(value, from){
        var old_store = Functions.clone(this.store);
        this.store.filterDates = SearchUtil.listChange(value, this.store.filterDates);
        if(from == 'mobile'){
            this.trigger(this.store);
            return;
        }
        this.filterSearch(old_store);
    },

    onCleanFilters(){
        this.store.filterSectors = [];
        this.store.filterRounds = [];
        this.store.filterLocations = [];
        this.store.filterDates = [];
        this.store.count = 0;
        this.store.list = [];
        this.store.filterLoad = true;
        this.trigger(this.store);
        this.loadFilter();
    },

    onComfirmFilters(){
        var old_store = Functions.clone(this.store);
        this.filterSearch(old_store);
    },

    onCancelFilters(){
        this.store.filterSectors = [];
        this.store.filterRounds = [];
        this.store.filterLocations = [];
        this.store.filterDates = [];
        this.trigger(this.store);
    },

    onRemoveFilterItem(type, id){

        if(type == 'sector'){
            for(var i in this.store.filterSectors){
                if(this.store.filterSectors[i] == id)
                    this.store.filterSectors.splice(i, 1)
            }
        }

        if(type == 'round'){
            for(var i in this.store.filterRounds){
                if(this.store.filterRounds[i] == id)
                    this.store.filterRounds.splice(i, 1)
            }
        }

        if(type == 'location'){
            for(var i in this.store.filterLocations){
                if(this.store.filterLocations[i] == id)
                    this.store.filterLocations.splice(i, 1)
            }
        }

        if(type == 'date'){
            for(var i in this.store.filterDates){
                if(this.store.filterDates[i] == id)
                    this.store.filterDates.splice(i, 1)
            }
        }

        var old_store = Functions.clone(this.store);
        this.filterSearch(old_store);
    },


    filterSearch(old_store){
        $('.modal').hide();
        this.store.filterLoad = true;
        this.trigger(this.store);
        this.store.list = [];
        var info = SearchUtil.getSearchInfo(this.store);
        var callback = function(result) {
            this.searchCallback(result)
        }.bind(this);

        var errorback = function(data){
            this.store = old_store;
            this.trigger(this.store)
        }.bind(this);

        return Http.ajaxSearch(info.params, info.url, callback, errorback);
    },


    clean(){
        this.store = {
            search:null,
            open: null,
            type: null,
            names:[],
            keywords: [],
            sectors:[],

            list: [],
            count: null,
            sort: 1,
            filterSectors:[],
            filterRounds:[],
            filterLocations:[],
            filterDates:[],

            loading: false,
            firstLoad: false
        };

        this.trigger(this.store);
    }


});

module.exports = SearchStore;