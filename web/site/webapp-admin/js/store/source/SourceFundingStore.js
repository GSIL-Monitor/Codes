var EventEmitter = require('events').EventEmitter;
var assign = require('object-assign');

var AppDispatcher = require('../../dispatcher/AppDispatcher');
var SourceConst = require('../../constant/SourceConst');

var CHANGE_EVENT = 'change';
var INVESOTR_CHANGE_EVENT = 'investor_change';

var store = {};
var funding_investor_store = {};

var source_arr = [];

function get(id, data) {
    store = {id: id, data: data};
    source_arr.push(store);
}

function updateStore(id){
    for(var i in source_arr){
        if(source_arr[i].id == id){
            store = source_arr[i];
        }
    }
}

function getFundingInvestor(id, data){
    funding_investor_store = {id: id, data: data};
}

var SourceFundingStore = assign({}, EventEmitter.prototype, {
    get: function(){
        return store;
    },

    getArr(){
        return source_arr;
    },

    getFundingInvestor(){
        return funding_investor_store;
    },

    emitChange: function() {
        this.emit(CHANGE_EVENT);
    },

    addChangeListener: function(callback) {
        this.on(CHANGE_EVENT, callback);
    },

    removeChangeListener: function(callback) {
        this.removeListener(CHANGE_EVENT, callback);
    },

    emitInvestorChange() {
        this.emit(INVESOTR_CHANGE_EVENT);
    },

    addInvestorChangeListener(callback) {
        this.on(INVESOTR_CHANGE_EVENT, callback);
    },

    removeInvestorChangeListener(callback) {
        this.removeListener(INVESOTR_CHANGE_EVENT, callback);
    }

});


AppDispatcher.register(function (action) {

    switch (action.actionType) {

        case SourceConst.GET_SOURCE_FUNDING:
            get(action.id, action.data);
            SourceFundingStore.emitChange();
            break;

        //case SourceConst.GET_SOURCE_FUNDING_FROM_STORE:
        //    updateStore(action.id);
        //    SourceFundingStore.emitChange();
        //    break;

        case SourceConst.GET_SOURCE_FUNDING_INVESTOR:
            getFundingInvestor(action.id, action.data);
            SourceFundingStore.emitInvestorChange();
            break;

        default:
            break;
    }
});


module.exports = SourceFundingStore;
