var Reflux = require('reflux');
var $ = require('jquery');
var NewsActions = require('../../action/company/NewsActions');
var Functions = require('../../../../react-kit/util/Functions');
var Http = require('../../../../react-kit/util/Http');

const NewsStore = Reflux.createStore({
    store: {
        update: false,
        showAll: false,
        list: [],
        news:{},
        companyId: null,
        newsId: null
    },

    init(){
        this.listenToMany(NewsActions);
    },

    onGet(id){
        this.store.companyId = id;
        var payload = {payload: {companyId: id}};
        var url = "/api/company/news/list";
        var callback = function(result){
            if (result.code == 0) {
                this.store.list = result.list;
            }else {}
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onShowAll(){
        if(this.store.showAll)
            this.store.showAll = false;
        else
            this.store.showAll = true;
        this.trigger(this.store);
    },

    onInitNewsDetail(companyId, newsId){
        var payload = {payload: {companyId: Number(companyId), newsId: Number(newsId)}};
        var url = "/api/company/news/get";
        var callback = function(result){
            if (result.code == 0) {
                this.store.news = result.news;
            }else {}
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    }

});


module.exports = NewsStore;