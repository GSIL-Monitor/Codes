var Reflux = require('reflux');
var $ = require('jquery');
var UserActions = require('./../action/UserActions');
var Http = require('../util/Http');

const UserStore = Reflux.createStore({
    store:{
        user: null,
        login: false,
        init: false,
        admin: false,
        org: null,
        mobileListShow : false
    },

    init: function () {
        this.listenToMany(UserActions);
    },

    onCheckLoginStatus() {
        var payload={payload:{}};
        var url = "/api/user/login/checkloginstatus";
        var callback = function(result){
            if(result.code == 0) {
                if(result.login == true){
                    this.store.login = true;
                    this.store.user = result.user;
                    this.store.admin = result.admin;
                    this.store.org = result.organization;
                }
            }
            this.store.init = true;
            this.trigger(this.store);
        }.bind(this);

        Http.ajaxAndMask(payload, url, callback);
    },

    onLogout() {
        var payload={ payload: {} };
        var url = "/api/user/login/logout";
        var callback = function(result) {
            if(result.code == 0) {
                this.store.login = false;
                this.store.user = null;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajaxAndMask(payload, url, callback);
    }

});

module.exports = UserStore;