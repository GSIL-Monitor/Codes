var Reflux = require('reflux');
var $ = require('jquery');
var MemberActions = require('../../action/company/MemberActions');
var Functions = require('../../../../react-kit/util/Functions');
var Http = require('../../../../react-kit/util/Http');

const MemberStore = Reflux.createStore({
    store: {
        update: false,
        showAll: false,
        list: [],
        selected: {},
        companyId: null
    },

    init(){
        this.listenToMany(MemberActions);
    },

    onGet(id){
        this.store.companyId = id;
        var payload = {payload: {id: id}};
        var url = "/api/company/member/list";
        var callback = function(result){
            if (result.code == 0) {
                this.store.list = result.members;
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

    onSelect(data){
        this.store.selected = data;
        this.trigger(this.store);
        $('#member-modal').show();
    },

});


module.exports = MemberStore;