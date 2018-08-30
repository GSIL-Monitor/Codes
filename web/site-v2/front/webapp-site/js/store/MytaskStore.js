var Reflux = require('reflux');
var $ = require('jquery');
var MytaskActions = require('../action/MytaskActions');

var Functions = require('../../../react-kit/util/Functions');
var Http = require('../../../react-kit/util/Http');
var TaskUtil = require('../util/TaskUtil');

const MytaskStore = Reflux.createStore({
    store:{
        task_type: null,
        cnt_todo_coldcall:0,
        cnt_todo_sponsoredcoldcall:0,
        cnt_todo_recommend:0,
        cnt_todo_self:0,

        cnt_total_task: 0,
        cnt_total_sponsoredcoldcall:0,
        cnt_total_self:0,


        filter_task_type: 'all',
        filter_task: 0,
        filter_sponsoredcoldcall:0,
        filter_self:4,

        list_task:[],
        list_sponsoredcoldcall:[],
        list_self:[],

        loading: false,
        firstLoad: false
    },

    init(){
        this.listenToMany(MytaskActions);
    },


    onGetTask(type, status){
        this.clean();
        if(Functions.isNull(type)) type = 'all';
        if(Functions.isNull(status)) status = 0;
        status = Number(status);
        this.store.filter_task_type = type;
        this.store.filter_task = status;

        this.onListMore(1);
    },


    onGetPublishTask(status){
        this.clean();
        if(Functions.isNull(status))  status = 0;
        status = Number(status);
        this.store.filter_sponsoredcoldcall = status;
        this.onListMore(2);
    },

    onGetDiscovery(status){
        this.clean();
        if(Functions.isNull(status))  status = 4;
        status = Number(status);
        this.store.filter_self = status;
        this.onListMore(23010);
    },

    onChangeType(type){
        window.location.href = '/#/task/'+TaskUtil.getTypeName(type);
    },


    onListMore(type){
        if(TaskUtil.isLoading(type, this.store)) return;
        this.store.loading = true;
        this.trigger(this.store);
        var params = TaskUtil.getLoadParam(type, this.store);
        var payload = {payload: {
                            type: params.type,
                            filter: Number(params.filter),
                            from: Number(params.start)
                        }};
        var url = params.url;
        var callback = function(result) {
            if (result.code == 0) {
                this.store.loading = false;
                this.store.firstLoad = true;
                this.store = TaskUtil.setResult(type, result, this.store);
            }
            this.trigger(this.store);

        }.bind(this);

        Http.ajax(payload, url, callback);
    },


    onChangeTaskFilterType(value){
        window.location.href = './#/task/'+value+ '/'+this.store.filter_task;
    },

    onChangeTaskFilterStatus(value){
        window.location.href = './#/task/'+this.store.filter_task_type+ '/'+value;
    },

    onChangePublishFilterStatus(value){
        window.location.href = './#/publish/'+value;
    },

    onChangeDiscoveryFilterStatus(value){
        window.location.href = './#/discovery/'+value;
    },


    clean(){
        this.store = {
            task_type: null,
            cnt_todo_coldcall:0,
            cnt_todo_sponsoredcoldcall:0,
            cnt_todo_recommend:0,
            cnt_todo_self:0,

            cnt_total_task: 0,
            cnt_total_sponsoredcoldcall:0,
            cnt_total_self:0,


            filter_task_type: 'all',
            filter_task: 0,
            filter_sponsoredcoldcall:0,
            filter_self:4,

            list_task:[],
            list_sponsoredcoldcall:[],
            list_self:[],

            loading: false,
            firstLoad: false
        };
        this.trigger(this.store);
    }

});

module.exports = MytaskStore;