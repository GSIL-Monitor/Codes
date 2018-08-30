var EventEmitter = require('events').EventEmitter;
var assign = require('object-assign');
var AppDispatcher = require('../dispatcher/AppDispatcher');
var Const = require('../constant/Const');
var CHANGE_EVENT = 'change';

var Functions = require('../../../react-kit/util/Functions');
var store = {};

function get(data) {
    store = data;
}


var SearchStore = assign({}, EventEmitter.prototype, {
    get(){
        return store;
    },

    emitChange() {
        this.emit(CHANGE_EVENT);
    },

    addChangeListener(callback) {
        this.on(CHANGE_EVENT, callback);
    },

    removeChangeListener(callback) {
        this.removeListener(CHANGE_EVENT, callback);
    }

});

AppDispatcher.register(function (action) {

    switch (action.actionType) {
        case Const.GET_SEARCH:
            get(action.data);
            SearchStore.emitChange();
            break;

        default:
            break;
    }
});


module.exports = SearchStore;
