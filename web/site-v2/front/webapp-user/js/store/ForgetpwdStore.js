var Reflux = require('reflux');
var $ = require('jquery');
var ForgetpwdActions = require('../action/ForgetpwdActions');
var Functions = require('../../../react-kit/util/Functions');

const ForgetpwdStore = Reflux.createStore({
    store:{
        email: '',
        password: '',
        sending: false,
        error: '',
        sent:false,
    },

    init: function () {
        this.listenToMany(ForgetpwdActions);
    },

    onNext(){
        this.store.sending = true;
        this.trigger(this.store);


        if(Functions.isNull(this.store.email)){
            this.store.sending = false;
            this.store.error = "请输入你的邮件地址";
            this.trigger(this.store);
        }else{
            var payload={
                payload: {
                    email:this.store.email,
                }
            };
            var url = "/api/user/login/forgetpwd";
            $.ajax({
                url: url,
                method: 'POST',
                data: JSON.stringify(payload),
                contentType:"application/json",
                cache: false,
                timeout: 5000,
                success: function(result) {
                    console.log(result)
                    if(result.code == 0) {
                        this.store.sent = true;
                    }
                    else{
                        this.store.error = "邮件地址不存在,请和管理员联系!";
                    }
                    this.store.sending = false;
                    this.trigger(this.store);
                }.bind(this),
                error: function(data) {
                    console.log(data);
                }.bind(this)
            });
        }
    },

    onReset(userId, oneTimePwd){
        this.store.sending = true;
        this.trigger(this.store);


        if(Functions.isNull(this.store.password)) {
            this.store.sending = false;
            this.store.error = "请输入你的密码";
            this.trigger(this.store);
        }
        else if(this.store.password.length < 8){
            this.store.sending = false;
            this.store.error = "密码长度不得少于8位!";
            this.trigger(this.store);
        }else{
            var payload={
                payload: {
                    password:this.store.password,
                    userId:userId,
                    oneTimePwd:oneTimePwd,
                }
            };
            console.log(payload);

            var url = "/api/user/login/resetpwd";
            $.ajax({
                url: url,
                method: 'POST',
                data: JSON.stringify(payload),
                contentType:"application/json",
                cache: false,
                timeout: 5000,
                success: function(result) {
                    console.log(result)
                    if(result.code == 0) {
                        this.store.sent = true;
                    }
                    else{
                        this.store.error = "重置失败!请重新操作";
                    }
                    this.store.sending = false;
                    this.trigger(this.store);
                }.bind(this),
                error: function(data) {
                    console.log(data);
                }.bind(this)
            });
        }
    },

    onChange(name, value) {
        //console.log(value);
        this.store[name] = value;
        this.trigger(this.store);
    },


});

module.exports = ForgetpwdStore;