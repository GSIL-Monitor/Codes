var Reflux = require('reflux');
var $ = require('jquery');
var SourceMemberActions = require('./SourceMemberActions')
var Config = require('../util/Config');


const SourceMemberStore = Reflux.createStore({
    members:null,

    init: function () {
        this.listenToMany(SourceMemberActions);
    },

    onGet: function(id){
        //console.log("id=" + id);
        var url = Config.pre_url()+"/member/source/list?id="+id;
        $.get(url, function (data) {
            //console.log(data);
            this.members = data;
            this.trigger(this.members);
        }.bind(this));
    },

});

module.exports = SourceMemberStore;