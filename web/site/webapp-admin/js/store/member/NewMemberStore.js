var EventEmitter = require('events').EventEmitter;
var assign = require('object-assign');

var AppDispatcher = require('../../dispatcher/AppDispatcher');
var Const = require('../../constant/Const');
var CHANGE_EVENT = 'change';

var store = {
    current:{},
    last:{
        id:-1,
        photo:"",
        name:"",
        education:"",
        work:"",
        workEmphasis:""
    }
};
initStore();

function initStore() {
    store["current"] = {
        id:-1,
        photo:"",
        name:"",
        education:"",
        work:"",
        workEmphasis:""
    };
}

function copyCurrentToLast() {
    current = store["current"];
    last = store["last"];
    for(var k in current){
        last[k] = current[k];
    }
}

function change(name, value) {
    var current = store["current"];
    for(var k in current){
        if (k == name) {
            current[k] = value.trim();
            break
        }
    }
}

const NewMemberStore = assign({}, EventEmitter.prototype, {
    get(){
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
        case Const.NEW_MEMBER_CHANGE:
            console.log(action);
            change(action.name, action.value);
            NewMemberStore.emitChange();
            break;

        case Const.NEW_MEMBER_CLEAN:
            initStore();
            NewMemberStore.emitChange();
            break;

        case Const.NEW_MEMBER_ADD:
            copyCurrentToLast();
            initStore();
            store["last"] = action.data.member;
            NewMemberStore.emitChange();
            break;

        default:
            break;
    }
});


module.exports = NewMemberStore;
