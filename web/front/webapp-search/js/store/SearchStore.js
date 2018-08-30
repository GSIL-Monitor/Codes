var EventEmitter = require('events').EventEmitter;
var assign = require('object-assign');
var AppDispatcher = require('../dispatcher/AppDispatcher');
var Const = require('../constant/Const');
var CHANGE_EVENT = 'change';

var Functions = require('../../../react-kit/util/Functions');
var store = [];
var sort = 1;
var search = "";

function get(data) {
    store = data;
}

function changeSort(data){
    sort = data;
}

function changeSearch(data){
    search = data;
}


var SearchStore = assign({}, EventEmitter.prototype, {
    get(){
        return store;
    },

    getSort(){
        return sort;
    },

    getSearch(){
        return search;
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

        case Const.CHANGE_SORT:
            changeSort(action.value);
            SearchStore.emitChange();
            break;

        case Const.CHANGE_SEARCH:
            changeSearch(action.data);
            SearchStore.emitChange();
            break;

        default:
            break;
    }
});


module.exports = SearchStore;
