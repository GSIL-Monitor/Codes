var AppDispatcher = require('../dispatcher/AppDispatcher');
var Const = require('../constant/Const');
var Config = require('../../../react-kit/util/Config');
var HTTP = require('../util/Http');
var $ = require('jquery');

var SearchAction = {

    get(code) {
        var url = Config.preURLEndCompanyAPI()+"/company/overview?code="+code;
        HTTP.get(code, url, Const.GET_SEARCH);
    },

    changeSearch(value){
        AppDispatcher.dispatch({
            actionType: Const.CHANGE_SEARCH,
            data: value
        });
    },

    changeSort(value){
        AppDispatcher.dispatch({
            actionType: Const.CHANGE_SORT,
            value: value
        });
    }



};

module.exports = SearchAction;
