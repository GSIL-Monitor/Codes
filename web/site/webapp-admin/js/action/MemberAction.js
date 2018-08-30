var AppDispatcher = require('../dispatcher/AppDispatcher');
var Const = require('../constant/Const');
var Config = require('../util/Config');
var Http = require('../util/Http');
var $ = require('jquery');
var ActionUtil = require('./ActionUtil');

const MemberAction = {

    get(id) {
        var url = Config.pre_url()+"/member/get/all?id="+id;
        Http.get(id, url, Const.GET_MEMBERS);
    },

    change(id, name, value) {
        AppDispatcher.dispatch({
            actionType: Const.CHANGE_MEMBER,
            id: id,
            name: name,
            value: value
        });
    },

    chooseMember(idx) {
        AppDispatcher.dispatch({
            actionType: Const.CHOOSE_MEMBER,
            idx: idx,
        });
    },

    update(data) {
        //console.log(data);
        var url = Config.pre_url()+"/member/update";
        Http.put(url, Const.UPDATE_MEMBER, data, '更新成功');
    },

    delete: function(data) {
        var url = Config.pre_url()+"/member/delete";
        Http.put(url, Const.DELETE_MEMBER_REL, data, '成功删除成员与公司的关联记录')
    }

};


module.exports = MemberAction;
