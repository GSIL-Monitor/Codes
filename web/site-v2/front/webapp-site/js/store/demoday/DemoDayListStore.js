var Reflux = require('reflux');
var $ = require('jquery');
var DemoDayListActions = require('../../action/demoday/DemoDayListActions');
var Functions = require('../../../../react-kit/util/Functions');
var Http = require('../../../../react-kit/util/Http');
var DemoDayUtil = require('../../util/DemoDayUtil');

const DemoDayListStore = Reflux.createStore({
    store: {
        list: [],
        selectedDemoDay: null
    },

    init(){
        this.listenToMany(DemoDayListActions);
    },

    onGetList(){
        var payload = {payload: {}};
        var url = "/api/company/demoday/list";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.list = result.list;
                if(result.list.length > 0 && this.store.selectedDemoDay == null){
                    this.store.selectedDemoDay = result.list[0];
                }
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajaxAndMask(payload, url, callback);
    },

    onHoverDemoDay(data){
        this.store.selectedDemoDay = data;
        this.trigger(this.store);
    }

    //onUnSelectDemoDay(){
    //    this.store.selectedDemoDay = null;
    //    this.trigger(this.store);
    //},

});

module.exports = DemoDayListStore;