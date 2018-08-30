var Reflux = require('reflux');
var $ = require('jquery');

var SettingActions = require('../../action/user/SettingActions');

var UserUtil = require('../../util/UserUtil');
var Functions = require('../../../../react-kit/util/Functions');
var Http = require('../../../../react-kit/util/Http');

const UserStore = Reflux.createStore({
    store:{
        sectors: [],
        selectedSectors: [],
        oldSectors: [],
        setting: {},
        recommendNum: 0,
        oldRecommendNum: 0
    },

    init() {
        this.listenToMany(SettingActions);
    },

    getSectors(){
        var payload = {payload: {}};
        var url = "/api/company/sector/list";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.sectors = result.sectors;
                this.trigger(this.store);
            }
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onSelectSector(data) {
        this.store.selectedSectors = UserUtil.listChange(data, this.store.selectedSectors);
        this.trigger(this.store);
    },


    onInit(){
        this.getSectors();
        var payload = {payload: {}};
        var url = "/api/user/setting/get";
        var callback = function (result) {
            if(result.code == 0){
                this.store.selectedSectors = [];
                this.store.oldSectors = [];
                if(result.sectors != null){
                    var sectors = result.sectors;
                    for(var i in sectors){
                        this.store.selectedSectors.push(sectors[i].sectorId);
                    }
                }
                this.store.oldSectors = Functions.clone(this.store.selectedSectors);

                if(result.setting == null) {
                    this.store.setting  = {};
                }else{
                    this.store.setting = result.setting;
                    this.store.recommendNum = result.setting.recommendNum;
                    this.store.oldRecommendNum = result.setting.recommendNum;
                }
            }
            this.trigger(this.store)
        }.bind(this);
        Http.ajax(payload, url, callback);
    },

    onUpdate(){
        var update = this.store.selectedSectors;
        var old = this.store.oldSectors;
        console.log(update);
        console.log(old);
        var newIds = UserUtil.getNewIds(update, old);
        var deleteIds = UserUtil.getDeleteIds(update, old);

        var payload = {payload: {recommendNum: Number(this.store.recommendNum),
                            newIds: newIds, deleteIds: deleteIds }};
        var url = "/api/user/setting/updateAll";
        var callback = function (result) {
            if(result.code == 0){
                this.store.setting.recommendNum = this.store.recommendNum;
                this.store.oldRecommendNum = this.store.setting.recommendNum;
                this.store.oldSectors = Functions.clone(this.store.selectedSectors);
                $('.hint').html('已更新').show().fadeOut(2000);
            }
            this.trigger(this.store)
        }.bind(this);
        Http.ajax(payload, url, callback);
    },


    onChangeRecommendNum(value){
        var reg = new RegExp("^[0-9]{0,2}$");
        if(reg.test(value)){
            //console.log(value);
            this.store.recommendNum = value;
            this.trigger(this.store);
        }
    }

});

module.exports = UserStore;