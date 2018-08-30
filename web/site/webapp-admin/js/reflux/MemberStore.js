var Reflux = require('reflux');
var $ = require('jquery');
var MemberActions = require('./MemberActions')
var Config = require('../util/Config');

function createBlankMember() {
    return {
        id:-1,
        photo:"",
        name:"",
        education:"",
        work:"",
        workEmphasis:""
    };
}

function change(name, value) {
    var current = MemberStore["current"];
    for(var k in current){
        if (k == name) {
            current[k] = value;
            break
        }
    }
}

const MemberStore = Reflux.createStore({
    current:createBlankMember(),
    last:createBlankMember(),

    init: function () {
        this.listenToMany(MemberActions);
    },

    onGet: function(id){
        //console.log("id=" + id);
        var url = Config.pre_url()+"/member/get?id="+id;
        $.get(url, function (data) {
            //console.log("<" + data + ">");
            this.current = data;
            this.trigger(this.current);
        }.bind(this));
    },

    onChange: function (name,value) {
        //console.log("onChange");
        change(name,value);
        this.trigger(this.current);
    },

    onAdd: function () {
    },

    onUpdate: function () {
        var url = Config.pre_url()+"/member/updatemember";
        var hint = '成功更新创业者';
        $('.mask').show();
        $.ajax({
            url: url,
            method: 'PUT',
            data: JSON.stringify(this.current),
            contentType:"application/json",
            cache: false,
            timeout: 1000,
            success: function(result) {
                //console.log(result)
                this.current = result["member"];
                $('.hint').show()
                    .html(hint)
                    .delay(1500)
                    .hide(0);

                $('.mask').hide();

                this.trigger(this.current);
            }.bind(this),
            error: function(data) {
                console.log(data);
                $('.mask').hide();
            }.bind(this)
        });
    },

    onDelete: function () {
        var url = Config.pre_url()+"/member/deletemember";
        var hint = '成功删除创业者';
        $('.mask').show();
        $.ajax({
            url: url,
            method: 'PUT',
            data: JSON.stringify(this.current),
            contentType:"application/json",
            cache: false,
            timeout: 1000,
            success: function(result) {
                //console.log(result)
                this.current = null;
                $('.hint').show()
                    .html(hint)
                    .delay(1500)
                    .hide(0);

                $('.mask').hide();

                this.trigger(this.current);
            }.bind(this),
            error: function(data) {
                console.log(data);
                $('.mask').hide();
            }.bind(this)
        });
    },

});

module.exports = MemberStore;