var Reflux = require('reflux');
var $ = require('jquery');
var ProductActions = require('../../action/company/ProductActions');
var Functions = require('../../../../react-kit/util/Functions');
var Http = require('../../../../react-kit/util/Http');
var ProductUtil = require('../../util/ProductUtil');

const ProductStore = Reflux.createStore({
    store: {
        update: false,
        showAll: false,
        selectedType: 4000,
        types: [],

        total: {},
        website: {},
        weibo: {},
        wechat: {},
        ios:{},
        android:{},
        windowsPhone:{},
        pc: {},
        mac:{},
        other: {},

        list: [],
        count: 0,
        companyId: null,

        artifact: null,
        //缓存数据，方便setResult
        alexaList: [],
        sanliulingList: [],
        baiduList: [],
        wandoujiaList: [],
        myappList: [],
        iosList: []
    },

    init(){
        this.listenToMany(ProductActions);
    },

    onGet(id){
        this.clean();
        this.store.companyId = id;
        var payload = {payload: {id: id}};
        var url = "/api/company/artifact/list";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.website = result.website;
                this.store.weibo = result.weibo;
                this.store.wechat = result.wechat;
                this.store.ios = result.iOS;
                this.store.android = result.android;
                this.store.windowsPhone = result.windowsPhone;
                this.store.pc = result.pc;
                this.store.mac = result.mac;
                this.store.other = result.other;

                var total = ProductUtil.getTotal(this.store);
                this.store.total = total;
                this.store.list = total.list;
                this.store.count = total.count;

                var types = result.types;
                var typeList = [4000];
                types = typeList.concat(types);
                this.store.types = types;
            } else {
            }
            //this.store.cachedList=[];
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onChangeType(type){
        this.store.selectedType = type;
        var params = ProductUtil.changeType(this.store);
        this.store.list = params.list;
        this.store.count = params.count;
        this.trigger(this.store);
    },

    onShowAll(){
        if (this.store.showAll)
            this.store.showAll = false;
        else
            this.store.showAll = true;
        this.trigger(this.store);
    },

    onGetTrends(id, type, expand){

        var payload = {
            payload: {
                companyId: this.store.companyId,
                artifactId: id,
                artifactType: type,
                expand: expand
            }
        };
        var url = "/api/company/artifact/trends";
        var callback = function (result) {
            if (result.code == 0) {
                if (Number(type) == 4010) {
                    this.store.alexaList = (null != result.alexaList ? result.alexaList : []);
                }
                else if (Number(type) == 4050) {
                    this.store.sanliulingList = (null != result.sanliulingList ? result.sanliulingList : []);
                    this.store.baiduList = (null != result.baiduList ? result.baiduList : []);
                    this.store.wandoujiaList = (null != result.wandoujiaList ? result.wandoujiaList : []);
                    this.store.myappList = (null != result.myappList ? result.myappList : []);
                }
                else if (Number(type) == 4040) {
                    this.store.iosList = (null != result.iosList ? result.iosList : []);
                }
            } else {
            }
            ProductUtil.setResult(id, type, this.store);
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onChangeNav(navType, data){
        var id = data.artifact.id;
        var list = this.store.list;
        for (var i  in list) {
            if (list[i].artifact.id == id) {
                list[i].navType = navType;
            }
        }
        //if (navType == 'trend') {
        //    //没有去数据库取数据，则trendsMonth为undefined
        //    if (!data.trendsMonth) {
        //        this.onGetTrends(data.artifact.id, data.artifact.type, 30);
        //    }
        //}
        this.trigger(this.store);
    },

    onChangeExpand(id,expand){
        var list = this.store.list;
        for (var i  in list) {
            if (list[i].artifact.id == id) {
                list[i].selected = expand
            }
        }
        this.trigger(this.store);
    },

    onChangeView(id, type){
        var list = this.store.list;
        for (var i  in list) {
            if (list[i].artifact.id == id) {
                list[i].trendsMonth.dataType = type;
                //if (list[i].selected == 'day') {
                //    list[i].trendsDay.dataType = type;
                //}
                //else if (list[i].selected == 'month') {
                //    list[i].trendsMonth.dataType = type;
                //}
            }
        }
        this.trigger(this.store);
    },

    clean(){
        this.store ={
            update: false,
            showAll: false,
            selectedType: 4000,
            types: [],

            total: {},
            website: {},
            weibo: {},
            wechat: {},
            ios:{},
            android:{},
            windowsPhone:{},
            pc: {},
            mac:{},
            other: {},

            list: [],
            count: 0,
            companyId: null,

            artifact: null,
            //缓存数据，方便setResult
            alexaList: [],
            sanliulingList: [],
            baiduList: [],
            wandoujiaList: [],
            myappList: [],
            iosList: []
        };

        this.trigger(this.store);
    }

});


module.exports = ProductStore;