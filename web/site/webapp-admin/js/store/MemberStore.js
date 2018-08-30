var EventEmitter = require('events').EventEmitter;
var assign = require('object-assign');

var AppDispatcher = require('../dispatcher/AppDispatcher');
var Const = require('../constant/Const');
var CHANGE_EVENT = 'change';

var store = {
    members:null,
    idx:0
};

function getMember(id){
    for (var i in store.members){
        if(store.members[i].member.id == id){
            return store.members[i];
        }
    }

    return null;
}


function change(id, name, value) {
    var m = getMember(id);

    for(var k in m.member){
        if (k == name) {
            m.member[k] = value.trim();
            break
        }
    }

    for(var k in m.rel){
        if (k == name) {
            m.rel[k] = value.trim();
            break
        }
    }
}

const MemberStore = assign({}, EventEmitter.prototype, {
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

        case Const.GET_MEMBERS:
            store.members = action.data;
            store.idx = 0
            MemberStore.emitChange();
            break;

        case Const.CHANGE_MEMBER:
            change(action.id, action.name, action.value);
            MemberStore.emitChange();
            break;

        case Const.CHOOSE_MEMBER:
            store.idx = action.idx;
            MemberStore.emitChange();
            break;

        case Const.UPDATE_MEMBER:
            MemberStore.emitChange();
            break;

        case Const.DELETE_MEMBER_REL:
            store.members.splice(store.idx,1);
            store.idx = 0
            MemberStore.emitChange();
            break;

        default:
            break;
    }
});


module.exports = MemberStore;
