var Reflux = require('reflux');
var $ = require('jquery');
var InvestorActions = require('./InvestorActions')
var Config = require('../util/Config');

function createBlankInvestor() {
    return {
        id:-1,
        name:"",
        type:10020,
        website:"",
        description:"",
        stage:"",
        field:"",
    };
}

const InvestorStore = Reflux.createStore({
    store:{
        current: createBlankInvestor(),
        last: createBlankInvestor(),
        sources:null,
    },

    init: function () {
        this.listenToMany(InvestorActions);
    },

    onGet: function(id){
        //console.log("id=" + id);
        var url = Config.pre_url()+"/investor/getwithsources?id="+id;
        $.get(url, function (data) {
            //console.log("<" + data + ">");
            this.store.current = data.investor;
            this.store.sources = data.sources;
            this.trigger(this.store);
        }.bind(this));
    },

    onChange: function (name,value) {
        //console.log(value);
        this.store.current[name] = value;
        this.trigger(this.store);
    },

    onClean: function() {
        this.store.current = createBlankInvestor();
        this.trigger(this.store);
    },

    onAdd: function () {
        var url = Config.pre_url()+"/investor/add";
        var hint = '成功增加投资人';
        $('.mask').show();
        $.ajax({
            url: url,
            method: 'PUT',
            data: JSON.stringify(this.store.current),
            contentType:"application/json",
            cache: false,
            timeout: 1000,
            success: function(result) {
                //console.log(result)
                $('.hint').show()
                    .html(hint)
                    .delay(1500)
                    .hide(0);
                $('.mask').hide();

                this.store.last = result["investor"];
                this.store.current = createBlankInvestor();
                this.trigger(this.store);
            }.bind(this),
            error: function(data) {
                console.log(data);
                $('.mask').hide();
            }.bind(this)
        });
    },

    onUpdate: function () {
        var url = Config.pre_url()+"/investor/update";
        var hint = '成功更新投资人';
        $('.mask').show();
        $.ajax({
            url: url,
            method: 'PUT',
            data: JSON.stringify(this.store.current),
            contentType:"application/json",
            cache: false,
            timeout: 1000,
            success: function(result) {
                //console.log(result)
                this.store.current = result["investor"];
                $('.hint').show()
                    .html(hint)
                    .delay(1500)
                    .hide(0);

                $('.mask').hide();

                this.trigger(this.store);
            }.bind(this),
            error: function(data) {
                console.log(data);
                $('.mask').hide();
            }.bind(this)
        });
    },

    onDelete: function () {
        var url = Config.pre_url()+"/investor/delete";
        var hint = '成功删除投资人';
        $('.mask').show();
        $.ajax({
            url: url,
            method: 'PUT',
            data: JSON.stringify(this.store.current),
            contentType:"application/json",
            cache: false,
            timeout: 1000,
            success: function(result) {
                //console.log(result)
                this.store.current = null;
                $('.hint').show()
                    .html(hint)
                    .delay(1500)
                    .hide(0);

                $('.mask').hide();

                this.trigger(this.store);
            }.bind(this),
            error: function(data) {
                console.log(data);
                $('.mask').hide();
            }.bind(this)
        });
    },

});

module.exports = InvestorStore;