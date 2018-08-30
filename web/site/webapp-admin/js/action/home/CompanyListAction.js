var AppDispatcher = require('../../dispatcher/AppDispatcher');
var Const = require('../../constant/Const');
var Config = require('../../util/Config');
var HTTP = require('../../util/Http');
var $ = require('jquery');

var CompanyListAction = {

    get: function(data) {
        var url = Config.pre_url()+"/company/list/get";
        HTTP.getList(url, data, Const.GET_COMPANY_LIST);
    }

};

module.exports = CompanyListAction;
