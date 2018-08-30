var AppDispatcher = require('../dispatcher/AppDispatcher');
var Const = require('../constant/Const');
var Config = require('../util/Config');
var Http = require('../util/Http');
var $ = require('jquery');
var ActionUtil = require('./ActionUtil');

const FundingAction = {

    get(id) {
        var url = Config.pre_url()+"/funding/get/all?id="+id;
        Http.get(id, url, Const.GET_FUNDING);
    },

    change(id, name, value) {
        AppDispatcher.dispatch({
            actionType: Const.CHANGE_FUNDING,
            id: id,
            name: name,
            value: value
        });
    },

    changeRound(id){
        AppDispatcher.dispatch({
            actionType: Const.CHANGE_ROUND,
            id: id
        });
    },

    updateFundingDB(data) {
        var url = Config.pre_url()+"/funding/update";
        Http.put(url, Const.UPDATE_FUNDING, data, '更新成功');
    },

    resetRound() {
        AppDispatcher.dispatch({
            actionType: Const.RESET_FUNDING
        });
    },

    changeAddFunding(name, value){
        AppDispatcher.dispatch({
            actionType: Const.CHANGE_ADD_FUNDING,
            name: name,
            value: value
        });
    },

    addFunding(data){
        $('#modal-add-funding').show();
    },

    addFundingDB(data){
        var url = Config.pre_url()+"/funding/add";
        Http.add(url, Const.ADD_FUNDING, data, '成功添加融资记录');
    },

    deleteFunding: function(data) {
        var url = Config.pre_url()+"/funding/delete";
        Http.put(url, Const.DELETE_FUNDING, data, '成功删除融资记录')
    },


    /************ Funding investor rel *************/

    changeInvestor(id){
        AppDispatcher.dispatch({
            actionType: Const.CHANGE_INVESTOR,
            id: id
        });
    },

    changeFIR(name, value){
        AppDispatcher.dispatch({
            actionType: Const.CHANGE_FIR,
            name: name,
            value: value
        });
    },

    changeAddFIR(name, value){
        AppDispatcher.dispatch({
            actionType: Const.CHANGE_ADD_FIR,
            name: name,
            value: value
        });
    },

    addFIRDB(data){
        var url = Config.pre_url()+"/funding/investor/add";
        Http.addAndReturnResult(url, Const.ADD_FIR, data, '成功添加融资投资方');
    },

    addFundingInvestor(){
        $('#modal-add-funding-investor').show();
    },

    updateFIRDB(data) {
        var url = Config.pre_url()+"/funding/investor/update";
        Http.put(url, Const.UPDATE_FIR, data, '更新相关投资方成功');
    },

    deleteModal(data){
            var content = '<p>'+data+'</p>';
            $('#modal-delete-fir').show();
            $('#modal-delete-fir > .modal-body > .modal-content').html(content);
    },

    deleteFIR(data){
        var url = Config.pre_url()+"/funding/investor/delete";
        Http.put(url, Const.DELETE_FIR, data, '成功删除关联投资方')
    }



};


module.exports = FundingAction;
