var AppDispatcher = require('../../dispatcher/AppDispatcher');
var SourceConst = require('../../constant/SourceConst');
var Config = require('../../util/Config');

var HTTP = require('../../util/Http');

var SourceFundingStore = require('../../store/source/SourceFundingStore');

var SourceFundingAction = {

    get(id) {
        var url = Config.pre_url()+"/funding/source/get?id="+id;
        HTTP.get(id, url, SourceConst.GET_SOURCE_FUNDING);
    },

    getFundingInvestorRel(id){
        if (id == null)
            return;

        var url = Config.pre_url()+"/funding/investor/source/get?id="+id;
        HTTP.get(id, url, SourceConst.GET_SOURCE_FUNDING_INVESTOR);
    }

};


module.exports = SourceFundingAction;
