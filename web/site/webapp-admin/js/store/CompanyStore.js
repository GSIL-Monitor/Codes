var EventEmitter = require('events').EventEmitter;
var assign = require('object-assign');
var AppDispatcher = require('../dispatcher/AppDispatcher');
var Const = require('../constant/Const');
var CHANGE_EVENT = 'change';

var Functions = require('../util/Functions');
var store = {};
var old_store={};

var recentStore = [];

function get(data) {
    store = data;
    updateOld(data);

}

function change(name, value) {

    for(var k in store){
        if (k == name)
            store[k] = value.trim();
    }
}

function updateOld(data) {
    //for (var k in data){
    //    old_store[k] = data[k]
    //}
    old_store = Functions.clone(data);
}

function reset(){
    for(var k in store){
        store[k] = old_store[k];
    }
}


var CompanyStore = assign({}, EventEmitter.prototype, {
    get: function(){
        return store;
    },

    getOld: function(){
        return old_store;
    },

    emitChange: function() {
        this.emit(CHANGE_EVENT);
    },

    addChangeListener: function(callback) {
        this.on(CHANGE_EVENT, callback);
    },

    removeChangeListener: function(callback) {
        this.removeListener(CHANGE_EVENT, callback);
    }

});

AppDispatcher.register(function (action) {

    switch (action.actionType) {
        case Const.GET_COMPANY:
            get(action.data);
            CompanyStore.emitChange();
            break;

        case Const.CHANGE_COMPANY:
            change(action.name, action.value);
            CompanyStore.emitChange();
            break;

        case Const.UPDATE_COMPANY:
            updateOld(action.data);
            //CompanyStore.emitChange();
            break;

        case Const.RESET_COMPANY:
            reset();
            CompanyStore.emitChange();
            break;

        default:
            break;
    }
});


module.exports = CompanyStore;
