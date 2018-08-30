var EventEmitter = require('events').EventEmitter;
var assign = require('object-assign');

var AppDispatcher = require('../../dispatcher/AppDispatcher');
var SourceConst = require('../../constant/SourceConst');

var CHANGE_EVENT = 'change';

var store = {};

function get(id, data) {
    store = data;
}

var SourceCompanyStore = assign({}, EventEmitter.prototype, {
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

        case SourceConst.GET_SOURCE_COMPANY:
            get(action.id, action.data);
            SourceCompanyStore.emitChange();
            break;

        default:
        // no op
    }
});


module.exports = SourceCompanyStore;
