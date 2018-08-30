var Reflux = require('reflux');
var $ = require('jquery');
var RecommendationActions = require('../action/RecommendationActions');

var Functions = require('../../../react-kit/util/Functions');
var Http = require('../../../react-kit/util/Http');

const RecommdationStore = Reflux.createStore({
    store:{
        list: null
    },

    init(){
        this.listenToMany(RecommendationActions);
    },

    onGet(){
        var payload = {payload: {}};
        var url = "/api/company/recommend/list";
        var callback = function(result){
            if(result.code == 0){
                this.store.list = result.list;
                this.trigger(this.store);
            }
        }.bind(this);

        Http.ajaxAndMask(payload, url, callback);
    },


});

module.exports = RecommdationStore;