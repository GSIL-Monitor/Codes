var AppDispatcher = require('../../dispatcher/AppDispatcher');
var SourceConst = require('../../constant/SourceConst');
var Config = require('../../util/Config');

var HTTP = require('../../util/Http');

var SourceCompanyAction = {

    get(id) {
        var url = Config.pre_url()+"/company/source/get?id="+id;
        HTTP.get(id, url, SourceConst.GET_SOURCE_COMPANY);

    }

};






module.exports = SourceCompanyAction;
