var Reflux = require('reflux');
var $ = require('jquery');
var ValidateDemodayActions = require('../../action/validation/ValidateDemodayActions');
var Functions = require('../../../../react-kit/util/Functions');
var Http = require('../../../../react-kit/util/Http');
var ValidateUtil = require('../../../../webapp-site/js/util/ValidateUtil');
const ValidateDemodayStore = Reflux.createStore({
    store:{
        name:{},
        submitEndDate:{},
        preScoreStartDate:{},
        preScoreEndDate:{},
        connectStartDate:{},
        connectEndDate:{},
        holdStartDate:{},
        holdEndDate:{},


    },

    init: function () {
        this.listenToMany(ValidateDemodayActions);
    },
    onChange(name){
        this.store[name].show = false;
        this.store[name].validation = true;
        this.trigger(this.store);
    },

    onName(value){
        if (null==value||value.trim() == '') {
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
        var url = "/api/admin/demoday/get";
        var callback = function (result) {
            if (result.code == 0 && result.demoday != null) {
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
    },

    onDate(name,value){
        if (null==value||value.trim() == '') {
            this.store[name].show = true;
            this.store[name].hint = '必填';
            this.store[name].validation = false;
            this.trigger(this.store);
            return;
        }
        else if(value.trim() == ''){
            return;
        }

        if(value.trim().length!=16){
            this.store[name].validation = false;
            this.store[name].hint = '请输入YYYY-MM-DD hh:mm日期格式';
            this.trigger(this.store);
            return;
        }
        var date = value.trim().substr(0,10);
        var code = ValidateUtil.checkDate(date);
        if (code > 0) {
            this.store[name].validation = false;
            switch (code) {
                case 1:
                    this.store[name].hint = '请输入YYYY-MM-DD hh:mm日期格式';
                    break;
                case 2:
                    this.store[name].hint = '请输入正确的年份';
                    break;
                case 3:
                    this.store[name].hint = '请输入正确的月份';
                    break;
                case 4:
                    this.store[name].hint = '请输入正确的日期';
                    break;
            }
        }
        else{
            this.store[name].validation = true;
        }
        this.trigger(this.store);
    }

});

module.exports = ValidateDemodayStore;