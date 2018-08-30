var AppDispatcher = require('../../dispatcher/AppDispatcher');
var Const = require('../../constant/Const');
var Config = require('../../util/Config');
var Http = require('../../util/Http');
var $ = require('jquery');
var ActionUtil = require('../ActionUtil');

const NewAction = {
    change(name, value) {
        AppDispatcher.dispatch({
            actionType: Const.NEW_MEMBER_CHANGE,
            name: name,
            value: value
        });
    },

    clean() {
        AppDispatcher.dispatch({
            actionType: Const.NEW_MEMBER_CLEAN
        });
    },

    add(data) {
        var url = Config.pre_url()+"/member/add";
        var type = Const.NEW_MEMBER_ADD;
        var hint = '成功添加创业者';
        Http.addAndReturnResult(url, type, data, hint);
    },
};


module.exports = NewAction;
