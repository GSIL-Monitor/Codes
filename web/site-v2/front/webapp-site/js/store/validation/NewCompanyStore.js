var Reflux = require('reflux');
var $ = require('jquery');
var NewCompanyActions = require('../../action/validation/NewCompanyActions');
var Functions = require('../../../../react-kit/util/Functions');
var ValidateUtil = require('../../util/ValidateUtil');
var Http = require('../../../../react-kit/util/Http');
var CreateCompanyStore = require('../CreateCompanyStore');
var ValidateUtil = require('../../util/ValidateUtil');


const NewCompanyStore = Reflux.createStore({
    store: {
        name: {},
        fullName: {},
        date: {},
        brief: {},
        investment: {},
        shareRatio: {},
        preMoney: {},
        postMoney: {},
        phone: {},
        round: {},
        sector: {},
        product: {},
        locationId: {},
        files: {},

        searchList: []
    },

    init(){
        this.listenToMany(NewCompanyActions);
    },
    clean(){
        this.store.name = {};
        this.store.fullName = {};
        this.store.date = {};
        this.store.brief = {};
        this.store.investment = {};
        this.store.shareRatio = {};
        this.store.preMoney = {};
        this.store.postMoney = {};
        this.store.phone = {};
        this.store.round = {};
        this.store.sector = {};
        this.store.product = {};
        this.store.locationId = {};
        this.store.files = {};
        this.trigger(this.store)

    },

    onGetInitData(){
        this.trigger(this.store);
    },

    onChange(name){
        this.store[name].show = false;
        this.store[name].validation = true;
        this.trigger(this.store);
    },

    onName(value){
        if (value.trim() == '') {
            this.store.name.show = true;
            this.store.name.hint = '必填';
            this.store.name.validation = false;
            this.trigger(this.store);
            return;
        }
        this.store.name.show = true;
        this.store.name.hint = '正在检查...';
        this.store.name.validation = true;
        this.trigger(this.store);

        this.search(value);

        var payload = {payload: {name: value.trim(), id: 'name'}};
        var url = "/api/company/get";
        var callback = function (result) {
            if (result.code == 0 && result.companies != null && result.companies.length > 0) {
                this.store.name.hint = '名称已存在';
                this.store.name.validation = false;
            }
            else {
                this.store.name.hint = 'usable';
                this.store.name.validation = true;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    search(value){
        var payload = {data: value, field: "name"};
        var url = "/api/search/complete";
        var callback = function (result) {
            this.store.searchList = result.name;
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onFullName(value){
        if (value.trim() == '') {
            return;
        }
        this.store.fullName.show = true;
        this.store.fullName.hint = '正在检查...';
        this.store.fullName.validation = true;
        this.trigger(this.store);

        var payload = {payload: {name: value.trim(), id: 'fullName'}};
        var url = "/api/company/get";
        var callback = function (result) {
            if (result.code == 0 && result.companies != null && result.companies.length > 0) {

                this.store.fullName.hint = '名称已存在';
                this.store.fullName.validation = false;
            }
            else {
                this.store.fullName.hint = 'usable';
                this.store.fullName.validation = true;
            }
            this.trigger(this.store);
        }.bind(this)

        Http.ajax(payload, url, callback);
    },

    onDate(value){
        if (value.trim() == '') {
            return;
        }

        var code = ValidateUtil.checkDate(value.trim());
        if (code > 0) {
            this.store.date.validation = false;
            switch (code) {
                case 1:
                    this.store.date.hint = '请输入YYYY-MM-DD日期格式';
                    break;
                case 2:
                    this.store.date.hint = '请输入正确的年份';
                    break;
                case 3:
                    this.store.date.hint = '请输入正确的月份';
                    break;
                case 4:
                    this.store.date.hint = '请输入正确的日期';
                    break;
            }
        }
        this.trigger(this.store);
    },

    onBrief(value){
        if (value.trim() == '') {
            this.store.brief.hint = '必填';
            this.store.brief.validation = false;
            this.trigger(this.store);
        }
    },

    onInvestment(name, value){
        var value = value.trim();
        if (ValidateUtil.validateMoney(value)) {
            this.onChange(name);
            this.store.investment.show = false;
            this.store.investment.validation = true;
        }
        else {
            this.store.investment.show = true;
            this.store.investment.validation = false;
            this.store.investment.hint = '请输入正整数'
        }
        this.trigger(this.store)

    },

    onShareRatio(name, value){
        var value = value.trim();
        if (ValidateUtil.validateShares(value)) {
            if (value >= 0 && value <= 100) {
                this.onChange(name);
                this.store.shareRatio.show = false;
                this.store.shareRatio.validation = true;
            }
            else {
                this.store.shareRatio.show = true;
                this.store.shareRatio.validation = false;
                this.store.shareRatio.hint = '0-100的数字'
            }

        }
        else {
            this.store.shareRatio.show = true;
            this.store.shareRatio.validation = false;
            this.store.shareRatio.hint = '0-100的数字'
        }
        this.trigger(this.store)

    },

    onRemindInvestment(){
        this.store.investment.show = true;
        this.store.investment.validation = false;
        this.store.investment.hint = '请先输入融资金额'
        this.trigger(this.store);
    },

    onPreMoney(name, value){
        var value = value.trim();
        if (ValidateUtil.validateMoney(value)) {
            this.onChange(name);
            this.store.preMoney.show = false;
            this.store.preMoney.validation = true;
        }
        else {
            this.store.preMoney.show = true;
            this.store.preMoney.validation = false;
            this.store.preMoney.hint = '请输入数字'
        }
        this.trigger(this.store);
    },

    onPostMoney(name, value){
        var value = value.trim();
        if (ValidateUtil.validateMoney(value)) {
            this.onChange(name);
            this.store.postMoney.show = false;
            this.store.postMoney.validation = true;
        }
        else {
            this.store.postMoney.show = true;
            this.store.postMoney.validation = false;
            this.store.postMoney.hint = '请输入数字'
        }
        this.trigger(this.store);
    },

    onPhone(name, value){
        var value = value.trim();
        if (ValidateUtil.checkNumber(value) && value.length == 11) {
            this.onChange(name);
            this.store.phone.show = false;
            this.store.phone.validation = true;
        }
        else {
            this.store.phone.show = true;
            this.store.phone.validation = false;
            this.store.phone.hint = '请输入正确号码'
        }
        this.trigger(this.store);
    },

    onRound(round){
        if (round.trim() == '') {
            this.store.round.show = true;
            this.store.round.validation = false;
            this.trigger(this.store);
        }
        else {
            this.onChange('round');
        }
    },

    onSector(sector){
        if (sector == null || sector == -1) {
            this.store.sector.show = true;
            this.store.sector.validation = false;
            this.trigger(this.store);
        }
        else {
            this.onChange('sector');
        }
    },

    onProduct(product){
        if (product == null || product.length == 0) {
            this.store.product.show = true;
            this.store.product.validation = false;
            this.store.product.hint = '请选择产品';
            this.trigger(this.store);
        }
        else {
            this.onChange('product');
        }
    },

    onProductWebsite(link){
        if (!ValidateUtil.validateURL(link)) {
            this.store.product.show = true;
            this.store.product.validation = false;
            this.store.product.hint = '网站链接不合法';
            this.trigger(this.store);
        } else {
            this.onChange('product');
        }
    },

    onLocationId(locationId){
        if (locationId == null) {
            this.store.locationId.show = true;
            this.store.locationId.validation = false;
            this.store.locationId.hint = '必填';
            this.trigger(this.store);
        }
        if (!Number(locationId)) {
            this.store.locationId.show = true;
            this.store.locationId.validation = false;
            this.store.locationId.hint = '请选择地址';
            this.trigger(this.store);
        }
        else {
            this.onChange('locationId');
        }
    },

    onUploadBp(length){
        if (length == 0) {
            this.store.files.show = true;
            this.store.files.validation = false;
            this.store.files.hint = '请上传bp';
            this.trigger(this.store);
        }
        else {
            this.onChange('files');
        }
    }

});


module.exports = NewCompanyStore;