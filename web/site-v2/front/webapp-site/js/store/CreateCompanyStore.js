var Reflux = require('reflux');
var $ = require('jquery');

var CreateCompanyActions = require('../action/CreateCompanyActions');

var Functions = require('../../../react-kit/util/Functions');
var Http = require('../../../react-kit/util/Http');
var CreateCompanyUtil = require('../util/CreateCompanyUtil');
var ValidateStore = require('../store/validation/NewCompanyStore');


const CreateCompanyStore = Reflux.createStore({
    store: {
        company: CreateCompanyUtil.createBlankCompany(),
        member: CreateCompanyUtil.createBlankMember(),
        location: "",
        saved: false,
        files: [],
        existCompany: null,
        error: 0,
        productTypes: [4010, 4020, 4030, 4040, 4050, 4099],
        productList: [],
        teamSize: "",
        newTags: [],
        add: false,
        parentSectors: [],
        subSectors: [],
        parentSectorId: null,
        subSectorId: null,
        coldcallId: null,
        demodayId: null,
        year: null,
        month: null,
        source:null,
        note: null
    },

    init(){
        this.listenToMany(CreateCompanyActions);
    },

    onGetInitData(coldcallId, demodayId){
        this.store.coldcallId = coldcallId;
        this.store.demodayId = demodayId;
        this.onGetSector();
        if (coldcallId) {
            this.getColdcallFilse(coldcallId);
        }
        this.trigger(this.store);
    },

    getColdcallFilse(coldcallId){
        var payload = {payload: {coldcallId: coldcallId}};
        var url = 'api/company/coldcall/detail';
        var callback = function (result) {
            if (result.code == 0) {
                for (var i in result.files) {
                    var file = {fileName: null, gridId: null};
                    file.fileName = result.files[i].filename;
                    file.gridId = result.files[i].link;
                    this.store.files.push(file);
                }
                this.trigger(this.store);
            }

        }.bind(this);
        Http.ajax(payload, url, callback);
    },

    onChange(name, value) {
        this.store.company[name] = value;
        if (name == 'investment' || name == 'shareRatio') {
            this.onUpdatePrePostMoney();
        }
        else {
            this.trigger(this.store);
        }
    },

    onClean() {
        this.store.company = CreateCompanyUtil.createBlankCompany(),
            this.store.member = CreateCompanyUtil.createBlankMember(),
            this.store.location = "";
        this.store.saved = false;
        this.store.files = [];
        this.store.productList = [];
        this.store.teamSize = "";
        this.store.newTags = [];
        this.store.add = false;
        this.store.parentSectors = [];
        this.store.subSectors = [];
        this.store.parentSectorId = null;
        this.store.subSectorId = null;
        this.store.year = null;
        this.store.month = null;
        this.store.source=null;
        this.store.note = null;
        this.trigger(this.store);
    },

    onAdd() {
        if (this.store.existCompany) {
            return;
        }
        if (!ValidateStore.store.name.validation) {
            $("#companyName").focus();
            return;
        }

        if (this.store.company.fullName.trim() != '' && !ValidateStore.store.fullName.validation) {
            $("#fullName").focus();
            return;
        }
        this.store.add = true;
        this.trigger(this.store);
        this.store.company.investment *= 10000;
        this.store.company.preMoney *= 10000;
        this.store.company.postMoney *= 10000;
        //默认是每个月的第一天
        if (this.store.year != null && this.store.month != null) {
            this.store.company.establishDate
                = this.store.year + '-' + this.store.month + '-01';
        }
        var payload = {
            payload: {
                company: this.store.company,
                member: this.store.member,
                productList: CreateCompanyUtil.getProductList(this.store.productList),
                tagIds: CreateCompanyUtil.getTagIds(this.store.newTags),
                sectorIds: [this.store.parentSectorId, this.store.subSectorId],
                coldcallId: this.store.coldcallId,
                demodayId: this.store.demodayId,
                files: this.store.files,
                source:Number(this.store.source),
                note: this.store.note
            }
        };
        var url = "/api/company/create/new";
        var callback = function (result) {
            if (result.code == 0) {
                if (this.store.coldcallId) {
                    window.location.href = "/#/coldcall/" + this.store.coldcallId + "/overview";
                }
                else if (this.store.demodayId) {
                    window.location.href = "/#/demoday/" + this.store.demodayId;
                }
                else {
                    window.location.href = "/#/company/" + result.company.code + "/overview";
                }
                this.onClean();
                ValidateStore.clean();
            }
            else {
                //company full name or name exists
                this.store.error = result.code;
                this.store.existCompany = result.company;
                this.store.add = false;
                $('.hint').html('新增失败!').show().fadeOut(3000);
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onUpload(file){
        var url = '/api/company/file/upload';
        var fd = new FormData();
        fd.append('file', file);

        $.ajax({
            url: url,
            data: fd,
            processData: false,
            contentType: false,
            type: 'POST',
            success: function (result) {
                if (result.code == 0) {
                    var file = {
                        fileName: result.fileName,
                        gridId: result.gridId
                    };
                    this.store.files.push(file);
                }
                this.trigger(this.store);
            }.bind(this)
        });
    },

    onAddUploadedFile(file) {
        this.store.files.push(file);
        this.trigger(this.store);
    },

    onUpdatePrePostMoney(){
        var shareRatio = this.store.company.shareRatio.trim();
        var investment = this.store.company.investment.trim();
        if (investment != "" && shareRatio != "") {
            if (Number(shareRatio) > 0 && Number(shareRatio) <= 100) {
                this.store.company.postMoney = Math.round((investment / shareRatio) * 100);
                this.store.company.preMoney = this.store.company.postMoney - investment;
            }
        }
        else if (investment == "") {
            this.store.company.postMoney = "";
            this.store.company.preMoney = "";
            this.store.company.shareRatio = "";
        }
        else if (investment != "" && shareRatio == "") {
            this.store.company.postMoney = "";
            this.store.company.preMoney = "";
        }
        this.trigger(this.store);
    },


    onSelectProduct(value){
        var productList = this.store.productList;

        //var product = {selected: true};
        //if (productList.length == 0) productList.push(product);

        var product = {type: value, selected: true, name: this.store.company.name};
        if (productList.length == 0) {
            productList.push(product);
        }
        else {
            var flag = false;
            for (var i in productList) {
                if (value == productList[i].type) {
                    flag = true;
                    if (productList[i].selected) {
                        productList[i].selected = false;
                        productList[i].name = '';
                    }
                    else {
                        productList[i].selected = true;
                        productList[i].name = this.store.company.name;
                    }
                }
            }

            if (!flag) productList.push(product);
        }
        this.trigger(this.store);
    },

    onGetSector(){
        var payload = {};
        var url = '/api/company/sector/list';
        var callback = function (result) {
            if (result.code == 0) {
                this.store.parentSectors = result.sectors;
            } else {
            }
            this.trigger(this.store);
        }.bind(this);
        Http.ajax(payload, url, callback);
    },


    onAddSector(name, value){
        if (name == 'firstSelect') {
            this.store['firstSectorId'] = value;
            this.store['secondSectorId'] = "";
        }
        else if (name == 'secondSelect') {
            this.store['secondSectorId'] = value;

        }
        this.trigger(this.store);

    },

    onTeamSizeChange(teamSize, headCountMin, headCountMax){
        this.store.teamSize = teamSize;
        this.store.company['headCountMin'] = headCountMin;
        this.store.company['headCountMax'] = headCountMax;
        this.trigger(this.store);
    },

    onMemberChange(name, value){
        this.store.member[name] = value;
        this.trigger(this.store);
    },

    onDeleteNewTag(id){
        var tags = this.store.newTags;
        for (var i in tags) {
            if (id == tags[i].id) {
                tags.splice(i, 1);
            }
        }

        this.trigger(this.store);
    },

    onAddProduct(){
        this.store.productTypes.push(4099);
        this.trigger(this.store);
    },

    onAddProductName(type, value){

        var productList = this.store.productList;
        var product = {type: type, selected: true, name: value};
        if (productList.length == 0) {
            productList.push(product);
        }
        else {
            var flag = false;
            for (var i in productList) {
                if (type == productList[i].type) {
                    flag = true;
                    if (productList[i].selected) {
                        productList[i].name = value;
                        productList[i].selected = (value.trim() != '');
                    }
                    else {
                        productList[i].selected = true;
                        productList[i].name = value;
                    }
                }
            }

            if (!flag) productList.push(product);
        }
        this.trigger(this.store);
    },

    onDeleteFile(id){
        var list = this.store.files;
        for (var i in list) {
            if (id == i) {
                list.splice(i, 1);
            }
        }
        this.trigger(this.store);
    },

    // change parentSector
    onChangeSector(value){
        value = Number(value);
        this.store.parentSectorId = value;
        //父标签发生变化，子标签要清空
        this.store.subSectorId = null;
        this.onGetSubSectors(value);
        this.trigger(this.store);
    },

    onChangeSubSector(value){
        value = Number(value);
        this.store.subSectorId = value;
        this.trigger(this.store);
    },

    onGetSubSectors(id){
        var payload = {payload: {id: id}};
        var url = "/api/company/sector/second";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.subSectors = result.sectors;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    // change Company date
    onChangeEstablishDate(name, value){
        if (name == 'year') {
            this.store.year = value;
        }
        if (name == 'month') {
            this.store.month = value;
        }
        this.trigger(this.store);
    },

    onChangeSource(value){
        this.store.source=value;
        this.trigger(this.store);
    },

    onChangeNote(value){
        this.store.note = value;
        this.trigger(this.store);
    }
});

module.exports = CreateCompanyStore;