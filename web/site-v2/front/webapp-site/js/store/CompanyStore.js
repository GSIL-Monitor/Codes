var Reflux = require('reflux');
var $ = require('jquery');
var CompanyActions = require('../action/CompanyActions');
var Functions = require('../../../react-kit/util/Functions');
var CompanyUtil = require('../util/CompanyUtil');
var ValidateUtil = require('../util/ValidateUtil');
var Http = require('../../../react-kit/util/Http');

var DemoDayStore = require('./demoday/DemoDayStore');

const CompanyStore = Reflux.createStore({
    store: {
        update: false,
        updateCompany: null,
        updateSectors: [],
        updateTags: [],
        updateFootprints: [],
        updateFundings: [],
        updateDocuments: [],
        updateParentSector: {},
        updateSubSector: {},

        selectedFunding: {},
        selectedFIR: {},
        selectedFootprint: {},
        selectedMember: {},
        selectedJob: {},

        addSector: CompanyUtil.initSector(),
        addTag: CompanyUtil.initTag(),
        addFunding: CompanyUtil.initFunding(),
        addFootprint: CompanyUtil.initFootprint(),
        addFIR: CompanyUtil.initFIR(),
        newFIRFlag: false,

        addParentSectorId: null,
        addSubSectorId: null,


        newTags: [],
        newFundings: [],
        newFootprints: [],
        newDocuments: [],

        deleteTags: [],
        deleteFundings: [],
        deleteFootprints: [],
        deleteDocuments: [],
        deleteFiles: [],

        fundingAll: false,
        footprintAll: false,
        developAll: false,

        code: null,
        from: null,
        company: null,
        companyId: null,
        tags: [],
        footprints: [],
        fundings: [],
        documents: [],
        parentSector: {},
        subSector: {},
        parentSectors: [],
        subSectors: [],
        gongshangList: [],


        deleteTagFlag: false,
        loadDone: false,
        demodayId: null,

        updateDateYear: 0,
        updateDateMonth: 0
    },

    init(){
        this.listenToMany(CompanyActions);
    },

    onUpdate(){
        if (this.store.update)
            this.store.update = false;
        else {
            this.store.update = true;
            //this.onGetSector();
            //var parentSector = this.store.updateParentSector;
            //if(!Functions.isEmptyObject(parentSector)){
            //    this.onGetSubSectors(parentSector.id);
            //}
            //else{
            //    this.store.updateParentSector.id = 1;
            //    this.onGetSubSectors(1);
            //}
            //
            //if(Functions.isNull(this.store.updateCompany.currency)){
            //    this.store.updateCompany.currency = 3020;
            //}
            //
            //if(Functions.isNull(this.store.updateCompany.headCountMin)){
            //    this.store.updateCompany.headCountMin = 1;
            //    this.store.updateCompany.headCountMax = 15;
            //}
        }
        this.trigger(this.store);
    },

    onChangeCompany(name, value){
        this.store.updateCompany[name] = value;
        this.trigger(this.store);
    },


    onComfirm(){

        if (this.store.from == 'demodayAdd') {
            if (!CompanyUtil.validateFromDemoday(this.store)) return;
        } else {
            if (this.store.updateDateYear != 0 && this.store.updateDateMonth != 0) {
                this.store.updateCompany.establishDate
                    = this.store.updateDateYear + '-' + this.store.updateDateMonth + '-01';
            }
            if (this.store.validateLocation) {
                $('#company-warn > .warn-body > .warn-content').html('请完善公司地址');
                $('#company-warn').show();
                return;
            }
        }


        CompanyUtil.updateCompany(this.store);
        CompanyUtil.updateSector(this.store);
        CompanyUtil.updateTags(this.store);
        CompanyUtil.updateDocuments(this.store);

        //CompanyUtil.updateFootprints(this.store);
        CompanyUtil.updateFundings(this.store);
        this.store.update = false;
        this.store.company = Functions.clone(this.store.updateCompany);
        this.store.tags = Functions.clone(this.store.updateTags.concat(this.store.newTags));
        this.store.documents = Functions.clone(this.store.updateDocuments.concat(this.store.newDocuments));
        this.store.parentSector = Functions.clone(this.store.updateParentSector);
        this.store.subSector = Functions.clone(this.store.updateSubSector);
        this.store.fundings = Functions.clone(this.store.updateFundings);

        this.trigger(this.store);

        if (this.store.from == 'demodayAdd') {
            DemoDayStore.addDemodayCompany(this.store.demodayId, this.store.companyId);
            return;
        }

        $('.hint').html('已更新').show().fadeOut(3000);


    },

    /*********** delete *********/
    onDeleteTag(id){
        var tags = this.store.updateTags;
        for (var i in tags) {
            if (id == tags[i].id) {
                tags.splice(i, 1);
                this.store.deleteTags.push(id);
            }
        }

        this.trigger(this.store);
    },

    onDeleteFunding(id){
        var fundings = this.store.updateFundings;
        for (var i in fundings) {
            if (id == fundings[i].funding.id) {
                fundings.splice(i, 1);
                this.store.deleteFundings.push(id);
            }
        }

        this.trigger(this.store);
    },

    onDeleteFootprint(id){
        var footprints = this.store.updateFootprints;
        for (var i in footprints) {
            if (id == footprints[i].id) {
                footprints.splice(i, 1);
                this.store.deleteFootprints.push(id);
            }
        }

        this.trigger(this.store);
    },

    onDeleteDocument(id){
        var files = this.store.updateDocuments;
        for (var i in files) {
            if (id == files[i].id) {
                files.splice(i, 1);
                this.store.deleteDocuments.push(id);
            }
        }

        this.trigger(this.store);
    },


    /** delete New **/


        onDeleteNewTag(id){
        var tags = this.store.newTags;
        for (var i in tags) {
            if (id == tags[i].id) {
                tags.splice(i, 1);
            }
        }

        this.trigger(this.store);
    },

    onDeleteNewFootprint(id){
        var list = this.store.newFootprints;
        for (var i in list) {
            if (id == i) {
                list.splice(i, 1);
            }
        }

        this.trigger(this.store);
    },

    onDeleteNewDocument(id){
        var list = this.store.newDocuments;
        for (var i in list) {
            if (id == i) {
                list.splice(i, 1);
            }
        }

        this.trigger(this.store);
    },


    /****** selected ************/
        onSelectFunding(funding){
        this.store.selectedFIR = null;
        this.store.selectedFunding = Functions.clone(funding);
        this.trigger(this.store);
        $('#update-funding-modal').show();
    },

    onSelectFIR(fir){
        this.store.selectedFIR = fir;
        this.store.newFIRFlag = false;
        this.trigger(this.store);
    },

    onSelectFootprint(footprint){
        this.store.selectedFootprint = Functions.clone(footprint);
        this.trigger(this.store);
        $('#update-footprint-modal').show();
    },


    /** select & change **/

        onChangeSelectedFootprint(name, value){
        this.store.selectedFootprint[name] = value;
        this.trigger(this.store);
    },

    onUpdateSelectedFootprint(){
        var list = this.store.updateFootprints;
        var selected = this.store.selectedFootprint;
        for (var i in list) {
            if (selected.id == list[i].id) {
                list[i] = selected;
            }
        }

        this.trigger(this.store);
    },


    /******* add ************/

        onAddFootprint(){
        this.store = CompanyUtil.addFootprint(this.store);

        this.trigger(this.store);
    },

    onAddNewFIR(value){
        this.store.newFIRFlag = value;
        this.store.selectedFIR = null;
        this.trigger(this.store);
    },


    onAddUploadedFile(file) {
        var document = CompanyUtil.initDocument();
        document.companyId = this.store.companyId;
        document.link = file.gridId;
        document.name = file.fileName;
        document.type = 9010;
        this.store.newDocuments.push(document);
        this.trigger(this.store);
    },

    // add change
    onChangeNewFootprint(name, value){
        this.store.addFootprint[name] = value;
        this.trigger(this.store);
    },


    // change Company basic
    onChangeEstablishDate(name, value){
        if (name == 'year') {
            this.store.updateDateYear = value;
        }
        if (name == 'month') {
            this.store.updateDateMonth = value;
        }
        this.trigger(this.store);
    },

    onChangeSector(value){
        value = Number(value);
        this.store.updateParentSector.id = value;
        this.store.updateParentSector.sectorName =
            CompanyUtil.getSectorName(value, this.store.parentSectors);

        this.onGetSubSectors(value);
        this.trigger(this.store);
    },

    onChangeSubSector(value){
        value = Number(value);
        this.store.updateSubSector.id = value;
        this.store.updateSubSector.sectorName =
            CompanyUtil.getSectorName(value, this.store.subSectors);
        this.trigger(this.store);
    },


    onChangeCompanySector(value){
        value = Number(value);
        this.updateSector(value, this.store.parentSector.id);
        this.store.parentSector.id = value;
        this.store.parentSector.sectorName =
            CompanyUtil.getSectorName(value, this.store.parentSectors);

        this.onGetSubSectors(value);
        this.trigger(this.store);
    },

    onChangeCompanySubSector(value){
        value = Number(value);
        this.updateSubSector(value, this.store.subSector.id);
        this.store.subSector.id = value;
        this.store.subSector.sectorName =
            CompanyUtil.getSectorName(value, this.store.subSectors);

        this.trigger(this.store);
    },

    onChangeInvestment(value){
        if (ValidateUtil.validateMoney(value)) {
            this.store.updateCompany.investment = value;
        }
        else if (Functions.isNull(value)) {
            this.store.updateCompany.investment = value;
        }
        this.changeMoney();
    },

    onChangeShareRatio(value){
        if (ValidateUtil.validateMoney(value)) {
            this.store.updateCompany.shareRatio = value;
        }
        else if (Functions.isNull(value)) {
            this.store.updateCompany.shareRatio = value;
        }
        this.changeMoney();
    },

    onChangeMoney(name, value){
        if (ValidateUtil.validateMoney(value)) {
            this.store.updateCompany[name] = value;
            this.trigger(this.store);
        }
        else if (Functions.isNull(value)) {
            this.store.updateCompany[name] = value;
            this.trigger(this.store);
        }
    },

    onChangeHeadCount(value){
        var headCount = CompanyUtil.getHeadCounts(value);
        this.store.updateCompany.headCountMin = headCount.min;
        this.store.updateCompany.headCountMax = headCount.max;
        this.trigger(this.store);
    },


    changeMoney(){
        var company = this.store.updateCompany;
        var shareRatio = company.shareRatio;
        var investment = company.investment;
        if (shareRatio > 0 && investment > 0) {
            company.postMoney = Math.round((investment / shareRatio) * 100);
            company.preMoney = company.postMoney - investment;
        }
        else {
            company.postMoney = null;
            company.preMoney = null;
        }
        this.trigger(this.store);
    },


    /******  show all *********/
        onShowFundingAll(){
        if (this.store.fundingAll)
            this.store.fundingAll = false;
        else
            this.store.fundingAll = true;
        this.trigger(this.store);
    },

    onShowFootprintAll(){
        if (this.store.footprintAll)
            this.store.footprintAll = false;
        else
            this.store.footprintAll = true;
        this.trigger(this.store);
    },

    onShowDevelopAll(){
        if (this.store.developAll)
            this.store.developAll = false;
        else
            this.store.developAll = true;
        this.trigger(this.store);
    },


    /*********  get data  ************/

        onInit(code, from, id){
        this.store.code = code;
        this.store.from = from;
        if (from == 'demodayAdd') {
            this.store.update = true;
            this.store.demodayId = id;
        } else if (from == 'preScore' || from == 'score') {
            this.store.update = false;
            this.store.demodayId = id;
        } else {
            this.store.update = false;
        }

        this.onGetCompany(code);
    },

    onGetCompany(code){
        var payload = {payload: {code: code}};
        var url = "/api/company/basic";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.company = result.company;
                if (result.company != null) {
                    this.store.companyId = result.company.id;
                }
                this.store.companyDesc = result.companyDesc;

                if (result.sectors == null) result.sectors = [];
                if (result.tags == null) result.tags = [];
                if (result.footprints == null) result.footprints = [];
                if (result.fundings == null) result.fundings = [];

                this.store.parentSector = CompanyUtil.getParentSector(result.sectors);
                this.store.subSector = CompanyUtil.getSubSector(result.sectors);

                this.store.tags = result.tags;
                this.store.footprints = CompanyUtil.reverseFootprints(result.footprints);
                this.store.fundings = CompanyUtil.reverseFundings(result.fundings);

                //this.store.update = false;
                this.store.updateCompany = CompanyUtil.parseUpdateFunding(Functions.clone(this.store.company));
                this.store.updateParentSector = CompanyUtil.getParentSector(Functions.clone(result.sectors));
                this.store.updateSubSector = CompanyUtil.getSubSector(Functions.clone(result.sectors));

                this.store.updateTags = Functions.clone(this.store.tags);
                this.store.updateFootprints = Functions.clone(this.store.footprints);
                this.store.updateFundings = Functions.clone(this.store.fundings);

                this.store.newTags = [];
                this.store.newFundings = [];
                this.store.newFootprints = [];
                this.store.newDocuments = [];

                var updateDate = this.store.updateCompany.establishDate;
                if (updateDate != null) {
                    this.store.updateDateYear = updateDate.split('-')[0];
                    this.store.updateDateMonth = updateDate.split('-')[1];
                }

                //this.store.develops = CompanyUtil.sortDevelop(result.footprints, result.fundings);


                if (this.store.update) {
                    this.onGetSector();
                    var parentSector = this.store.updateParentSector;
                    if (!Functions.isEmptyObject(parentSector)) {
                        this.onGetSubSectors(parentSector.id);
                    }
                    //else{
                    //    this.store.updateParentSector.id = 1;
                    //    this.onGetSubSectors(1);
                    //}
                    //
                    //if(Functions.isNull(this.store.updateCompany.currency)){
                    //    this.store.updateCompany.currency = 3020;
                    //}
                    //
                    //if(Functions.isNull(this.store.updateCompany.headCountMin)){
                    //    this.store.updateCompany.headCountMin = 1;
                    //    this.store.updateCompany.headCountMax = 15;
                    //}
                }

                this.store.loadDone = true;

                if (this.store.from == 'demodayAdd' ||
                    this.store.from == 'preScore' ||
                    this.store.from == 'score') {
                    DemoDayStore.store.loadDone = true;
                    DemoDayStore.getDemodayCompany(this.store.demodayId, this.store.companyId);
                }
            }
            else {
                this.store.company = null;
                window.location.href = '/#/404';
            }
            this.trigger(this.store);

            //load others
            this.onGetSector();
            var parentSector = this.store.parentSector;
            if (!Functions.isEmptyObject(parentSector)) {
                this.onGetSubSectors(parentSector.id);
            }
            this.onGetDocument();
            this.getGongshang();

        }.bind(this);

        Http.ajaxAndMask(payload, url, callback);
    },

    onGetDocument(){
        var payload = {payload: {id: this.store.companyId}};
        var url = "/api/company/document/list";
        var callback = function (result) {
            if (result.code == 0) {
                if (result.documents == null) result.documents = [];
                this.store.documents = result.documents;
                this.store.updateDocuments = Functions.clone(this.store.documents);
            }
            else {
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onGetSector(){
        var payload = {payload: {}};
        var url = "/api/company/sector/list";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.parentSectors = result.sectors;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
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

    getGongshang(){
        this.store.gongshangList = [];
        var payload = {payload: {id: this.store.companyId}};
        var url = "/api/company/gongshang";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.gongshangList = result.list;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },


    /******** tag DB *********/
        onSearchTag(data){
        if (!this.store.deleteTagFlag)
            window.location.href = '/search/#/open/' + data;
    },

    onDeleteTagDB(id){
        this.store.deleteTagFlag = true;

        setTimeout(function () {
            CompanyStore.store.deleteTagFlag = false;
        }, 300);

        var payload = {payload: {tagId: Number(id), companyId: this.store.companyId}};
        var url = "/api/company/tag/delete/one";
        var callback = function (result) {
            if (result.code == 0) {
                var tags = this.store.tags;
                for (var i in tags) {
                    if (id == tags[i].id) {
                        tags.splice(i, 1);
                    }
                }
                this.store.updateTags = Functions.clone(tags);
                $('.hint').html('已删除').show().fadeOut(1000);
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onInsertTagDB(tag){
        console.log(tag);
        var payload = {payload: {tag: tag, companyId: this.store.companyId}};
        var url = "/api/company/tag/add/one";
        var callback = function (result) {
            if (result.code == 0) {
                var tags = this.store.tags;
                tags.push(tag);
                this.store.updateTags = Functions.clone(tags);
                $('.hint').html('已添加').show().fadeOut(1000);
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },


    /**** update sector  ***/
        updateSector(id, oldId){
        if (oldId == null && id == 0) return;
        var payload = {payload: {companyId: this.store.companyId, sectorId: Number(id), oldId: Number(oldId)}};
        var url = "/api/company/sector/update/one";
        var callback = function (result) {
            if (result.code == 0) {
                var sector = result.sector;
                this.store.updateParentSector = Functions.clone(sector);
                $('.hint').html('已更新行业').show().fadeOut(2000);
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    updateSubSector(id, oldId){
        if (oldId == null && id == 0) return;
        var payload = {payload: {companyId: this.store.companyId, sectorId: Number(id), oldId: Number(oldId)}};
        var url = "/api/company/sector/update/one";
        var callback = function (result) {
            if (result.code == 0) {
                var sector = result.sector;
                this.store.updateSubSector = Functions.clone(sector);
                $('.hint').html('已更新子行业').show().fadeOut(2000);
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    /**改变selected 的funding信息，改完后保存在updateFundings中**/
        onChangeSelectedFunding(name, value){
        if (name == 'investment' || name == 'preMoney' || name == 'postMoney') {
            if (ValidateUtil.validateMoney(value)) this.store.selectedFunding.funding[name] = value;
            else {
                $('.hint').html('请输入正整数').show().fadeOut(2000);
            }
        }
        else {
            this.store.selectedFunding.funding[name] = value;
        }
        this.trigger(this.store);
    },

    onUpdateFundingAndInvestor(type){
        CompanyUtil.updateFundingAndInvestor(this.store,type);
        this.trigger(this.store);
        if(type=="addFunding"){
            $('#add-funding-modal').hide();
        }else{
            $('#update-funding-modal').hide();
        }

    },

    onDeleteFIR(fir, type){
        CompanyUtil.deleteFIR(fir, this.store, type);
        this.trigger(this.store);
    },

    onChangeAddFIR(name, value){

        this.store.addFIR.fir[name] = value;
        this.trigger(this.store);
    },

    onAddNewFIRConfirm(type){

        if (this.store.selectedFIR && this.store.selectedFIR.investorId) {
            this.store.addFIR.investor.id = this.store.selectedFIR.investorId;
            this.store.addFIR.investor.name = this.store.selectedFIR.name;
            this.store.addFIR.fir.investorId = this.store.selectedFIR.investorId;
            this.store.addFIR.fir.fundingId = this.store.selectedFunding.funding.id;
            if (type == "addFunding") {
                this.store.addFunding.firList.push(this.store.addFIR);
            } else {
                this.store.selectedFunding.firList.push(this.store.addFIR);
            }
            this.trigger(this.store)
        } else {
            $('.hint').html('请选择投资方').show().fadeOut(2000);
        }
    },

    onChangeFunding(name, value){
        this.store.addFunding.funding[name] = value;
        this.trigger(this.store)
    }
});

module.exports = CompanyStore;