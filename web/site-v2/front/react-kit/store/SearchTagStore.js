var Reflux = require('reflux');
var $ = require('jquery');
var TagActions = require('../action/SearchTagActions');
var Http = require('../util/Http');
var SearchUtil = require('../util/SearchUtil');
var Functions = require('../util/Functions');

var CompanyStore = require('../../webapp-site/js/store/CompanyStore');
var CreateCompanyStore = require('../../webapp-site/js/store/CreateCompanyStore');

var NewCollectionStore = require('../../webapp-site/js/store/collection/NewCollectionStore');

const SearchTagStore = Reflux.createStore({
    store: {
        value: null,
        tag: null,
        tagId: null,
        //matches: [],
        hint: null,
        selected: null,
        from: null
    },

    init() {
        this.listenToMany(TagActions);
    },

    onInit(from){
        this.store.from = from;
        this.trigger(this.store);
    },


    onGet(value){
        if (Functions.isNull(value))
            return;
        this.store.value = value;

        var params = {data: value, field: 'keyword'};
        var url = '/api/search/complete';
        var callback = function (result) {
            this.store.hint = result;
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(params, url, callback);
    },

    onChange(value){
        this.store.selected = null;
        this.store.tag = value;
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

        if (value === 13) {
            this.onClickSearch();
        }

        if (value === 38 || value === 40) {
            result = SearchUtil.getTagSelected(value, this.store.selected, this.store.hint);
            this.store.selected = result;
            this.trigger(this.store);
        }

    },

    onClickSearch(){

        //if(this.store.selected == null) return null;

        if (this.store.from == 'company') {
            if (this.store.selected == null)
                this.store.selected = {name: this.store.value};
            CompanyStore.onInsertTagDB(this.store.selected);
        }

        if (this.store.from == 'updateCompany') {
            if (this.store.selected == null)
                this.store.selected = {name: this.store.value};
            CompanyStore.store.newTags = SearchUtil.doTagMatch(this.store, CompanyStore.store.newTags);
            CompanyStore.trigger(CompanyStore.store);
        }

        if (this.store.from == 'createCompany') {
            if (this.store.selected == null) {
                this.addNewTag();
            }else{
                CreateCompanyStore.store.newTags = SearchUtil.doTagMatch(this.store, CompanyStore.store.newTags);
                CreateCompanyStore.trigger(CreateCompanyStore.store);
            }
        }

        if (this.store.from == 'newCollection') {
            if (this.store.selected == null){
                this.getTag(this.store.value);
                return;
            }
            else
                NewCollectionStore.addNewTag(this.store.selected);
        }

        this.store.tag = null;
        this.trigger(this.store);
    },

    addNewTag(){
        var payload = { payload: {name: this.store.value}};
        var url = '/api/company/tag/new';
        var callback = function (result) {
            if (result.code == 0) {
                this.store.selected = result.tag;
                CreateCompanyStore.store.newTags = SearchUtil.doTagMatch(this.store, CompanyStore.store.newTags);
                CreateCompanyStore.trigger(CreateCompanyStore.store);
                this.store.selected == null
            }
        }.bind(this);

        Http.ajax(payload, url, callback);
    },


    getTag(value){
        var params = {payload:{name: value}};
        var url = '/api/company/tag/get';
        var callback = function(result) {
            if(result.code == 0){
                if(result.tag == null)
                    $('.hint').html('不存在该标签').show().fadeOut(3000);
                NewCollectionStore.addNewTag(result.tag);
            }else{
                $('.hint').html('不存在该标签').show().fadeOut(3000);
            }
        }.bind(this);

        Http.ajax(params, url, callback);
    }


});


module.exports = SearchTagStore;