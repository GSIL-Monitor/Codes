var AppDispatcher = require('../dispatcher/AppDispatcher');
var Const = require('../constant/Const');
var Config = require('../util/Config');
var HTTP = require('../util/Http');
var $ = require('jquery');

var CompanyAction = {

    get: function(id) {
        var url = Config.pre_url()+"/company/get/id?id="+id;
        HTTP.get(id, url, Const.GET_COMPANY);
    },

    change: function(name, value) {
        AppDispatcher.dispatch({
            actionType: Const.CHANGE_COMPANY,
            name: name,
            value: value
        });
    },

    updateDB: function(data) {
        var url = Config.pre_url()+"/company/update";
        HTTP.put(url, Const.UPDATE_COMPANY, data, '更新成功');
    },

    reset: function() {
        AppDispatcher.dispatch({
            actionType: Const.RESET_COMPANY
        });
    },

    delete: function(company) {
        AppDispatcher.dispatch({
            actionType: Const.DELETE_COMPANY,
            company: company
        });
    }

};


module.exports = CompanyAction;
