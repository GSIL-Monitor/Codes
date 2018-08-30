var Reflux = require('reflux');
var $ = require('jquery');
var UserHomeActions = require('../action/UserHomeActions');
var Functions = require('../../../react-kit/util/Functions');
var Http = require('../../../react-kit/util/Http');

const UserHomeStore = Reflux.createStore({
    store:{
        deal: null,
        score: null,
        cnt_task : 0,
        cnt_publish: 0,
        cnt_discovery: 0,
        type: null
    },

    init(){
        this.listenToMany(UserHomeActions);
    },

    onInit(type){
        this.store.type = type;
        this.onCountTODO();
    },

    onCountTODO(){
        var payload = {payload: {}};
        var url = "/api/company/mytask/counttodo";
        var callback = function(result){
            if(result.code == 0) {
                this.store.cnt_task = result.cnt_todo_coldcall + result.cnt_todo_recommend;
                this.store.cnt_publish = result.cnt_todo_sponsoredcoldcall;
                this.store.cnt_discovery=result.cnt_todo_self;
                this.trigger(this.store);
            }
        }.bind(this);

        Http.ajax(payload,url, callback);
    },

    onChangeTask(type){
        if(type == this.store.type) return;
        var link;
        if(type == 'task'){
            link = './#/';
        }else if(type == 'publish'){
            link = './#/publish/';
        }else{
            link = './#/discovery';
        }

        window.location.href = link;
    }


});

module.exports = UserHomeStore;