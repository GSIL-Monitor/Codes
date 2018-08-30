var AppDispatcher = require('../../dispatcher/AppDispatcher');
var SourceConst = require('../../constant/SourceConst');
var Config = require('../../util/Config');

var HTTP = require('../../util/Http');

var SourceMemberAction = {

    get(id) {
        var url = Config.pre_url()+"/member/source/get/all?id="+id;
        HTTP.get(id, url, SourceConst.GET_SOURCE_MEMBER);

    },

};


module.exports = SourceMemberAction;
