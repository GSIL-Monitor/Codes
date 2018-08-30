var Reflux = require('reflux');
var $ = require('jquery');
var UserActions = require('../action/UserActions');
var Functions = require('../../../react-kit/util/Functions');
var Http = require('../../../react-kit/util/Http');

var newUser = {username: "", password:""};


const UserStore = Reflux.createStore({
    store:{
        user: newUser,
        login: false,
        error: '',
        autoLogin: true,
        verified: false,
        returnurl: "",
        setting: false,
        grade:0
    },

    init: function () {
        this.listenToMany(UserActions);
    },

    onLogin(username, password){

        this.store.user.username = username;
        this.store.user.password = password;

        this.store.login = true;
        this.trigger(this.store);

        if(Functions.isNull(this.store.user.username)){
            this.store.login = false;
            this.store.error = "请输入用户名";
            this.trigger(this.store);
        }else if (Functions.isNull(this.store.user.password)){
            this.store.login = false;
            this.store.error = "请输入密码";
            this.trigger(this.store);
        }else{
            var payload={
                payload: {
                    email:this.store.user.username,
                    password:this.store.user.password,
                    autoLogin:this.store.autoLogin
                }
            };
            var url = "/api/user/login/verify";
            var callback = function(result) {
                if(result.code == 0) {
                    this.store.verified = true;
                    this.store.setting = result.setting;
                    this.store.grade = result.grade;
                }
                else{
                    var errors=['','账号或密码错误','账号已锁定','账号已失效'];
                    this.store.error = errors[result.code];
                }
                this.store.login = false;
                this.trigger(this.store);
            }.bind(this);

            Http.ajax(payload, url, callback);
        }



    },

    onChange(name, value) {
        this.store.user[name] = value;
        this.trigger(this.store);
    },

    onAutoLogin(value){
        this.store.autoLogin = value;
        this.trigger(this.store);
    },

    onSetReturnurl(returnurl) {
        this.store.returnurl= returnurl;
    }

});

module.exports = UserStore;