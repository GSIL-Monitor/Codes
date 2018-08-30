var EventEmitter = require('events').EventEmitter;
var assign = require('object-assign');
var AppDispatcher = require('../../dispatcher/AppDispatcher');
var Const = require('../../constant/Const');
var CHANGE_EVENT = 'change';

var Functions = require('../../util/Functions');
var store = [];

function get(data) {
    store = data;
}


var CompanyListStore = assign({}, EventEmitter.prototype, {
    get: function(){
        return store;
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
        case Const.GET_COMPANY_LIST:
            get(action.data);
            CompanyListStore.emitChange();
            break;

        default:
            break;
    }
});


module.exports = CompanyListStore;
