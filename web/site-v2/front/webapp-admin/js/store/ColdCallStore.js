var Reflux = require('reflux');
var $ = require('jquery');

var ColdCallActions = require('../action/ColdCallActions');

var Functions = require('../../../react-kit/util/Functions');
var Http = require('../../../react-kit/util/Http');
var ColdCallUtil = require('../util/ColdCallUtil');

const ColdCallStore = Reflux.createStore({
    store: {
        //0 unmatched ,1 matched
        coldCall_Type: null,
        total: null,
        unmatch_total: null,
        match_total: null,
        // match 和unmatch的cold
        matched_list: [],
        unmatched_list: [],
        pageSize: 10,
        loading:false
    },

    init: function () {
        this.listenToMany(ColdCallActions);
    },
    onGetInitData(type){
        this.clean();
        this.count();
        this.store.coldCall_Type = type;
        this.onListMore(type);
        this.trigger(this.store);

    },
    clean(){
        this.store.matched_list = [];
        this.store.unmatched_list = [];
    },
    /**get total numbers of coldcall**/
        count() {
        var payload = {payload: {}};
        var url = "/api/admin/coldCall/count";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.total = result.total;
                this.store.match_total = result.matched;
                this.store.unmatch_total = result.unmatched;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onListMore(type){
        if(ColdCallUtil.isLoading(type, this.store)) return;
        this.store.loading = true;
        var params = ColdCallUtil.getLoadParam(type, this.store);
        var payload = {
            payload: {
                pageSize: this.store.pageSize,
                from: params.start
            }
        };
        var url = params.url;
        var callback = function (result) {
            if (result.code == 0) {
                this.store.loading = false;
                ColdCallUtil.setResult(type, result, this.store);
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onChangeType(type){
        if (type == 0) {
            window.location.href = '/admin/#/coldCall/unmatch';
        }
        else if (type == 1) {
            window.location.href = '/admin/#/coldCall/match';
        }
    }

});

module.exports = ColdCallStore;