var Reflux = require('reflux');
var $ = require('jquery');
var CompanyInfoActions = require('./../action/CompanyInfoActions');
var CompanyUtil = require('../../webapp-site/js/util/CompanyUtil');
var Http = require('../../react-kit/util/Http');

const CompanyInfoStore = Reflux.createStore({
    store:{
        code: null,
        company: null,
        parentSector: null,
        subSector: null,
        tags: [],
        footprints: [],
        fundings: []
    },

    init() {
        this.listenToMany(CompanyInfoActions);
    },

    onInit(code){
        this.store.code = code;
        this.trigger(this.store);
    },

    onGetCompany(code){
        //this.countPosition();
        this.clean();
        var payload ={payload: {code: code}};
        var url = "/api/company/basic";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.company = result.company;
                if(result.company != null){
                    this.store.companyId = result.company.id;
                }
                if(result.sectors == null) result.sectors = [];
                if(result.tags == null) result.tags = [];
                if(result.footprints == null) result.footprints = [];
                if(result.fundings == null) result.fundings = [];

                this.store.parentSector = CompanyUtil.getParentSector(result.sectors);
                this.store.subSector = CompanyUtil.getSubSector(result.sectors);

                this.store.tags = result.tags;
                this.store.footprints = CompanyUtil.reverseFootprints(result.footprints);
                this.store.fundings = CompanyUtil.reverseFundings(result.fundings);
            }
            this.trigger(this.store);

        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    clean(){
        this.store = {  company: null,
                        parentSector: null,
                        subSector: null,
                        tags: [],
                        footprints: [],
                        fundings: []
                     };
        this.trigger(this.store);
    },

    countPosition(){
        var offset = $('.item-head > div.match-info').offset();
        if(offset != undefined){
            $('.company-popover').css('margin-left', '-'+offset.left*0.5+'px');
        }else{
            $('.company-popover').css('margin-left', '0');
        }
    }
});

module.exports = CompanyInfoStore;