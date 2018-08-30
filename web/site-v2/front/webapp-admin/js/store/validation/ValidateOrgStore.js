var Reflux = require('reflux');
var $ = require('jquery');
var ValidateOrgActions = require('../../action/validation/ValidateOrgActions');
var Functions = require('../../../../react-kit/util/Functions');
var Http = require('../../../../react-kit/util/Http');

const ValidateOrgStore = Reflux.createStore({
    store:{
        name:{},
    },

    init: function () {
        this.listenToMany(ValidateOrgActions);
    },
    onChange(name){
        this.store[name].show = false;
        this.store[name].validation = true;
        this.trigger(this.store);
    },

    onName(value){
        if (value.trim() == '') {
            this.store.name.show = true;
            this.store.name.hint = '必填';
            this.store.name.validation = false;
            this.trigger(this.store);
            return;
        }
        this.store.name.show = true;
        this.store.name.hint = '正在检查...';
        this.store.name.validation = true;
        this.trigger(this.store);

        var payload = {payload: {name: value.trim()}};
        var url = "/api/admin/org/get";
        var callback = function (result) {
            if (result.code == 0 && result.org != null) {
                this.store.name.hint = '名称已存在';
                this.store.name.validation = false;
            }
            else {
                this.store.name.hint = 'usable';
                this.store.name.validation = true;
            }
            this.trigger(this.store);
        }.bind(this)

        Http.ajax(payload, url, callback);
    }
});

module.exports = ValidateOrgStore;