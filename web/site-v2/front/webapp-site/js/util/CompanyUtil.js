var $ = require('jquery');
var Http = require('../../../react-kit/util/Http');
var Functions = require('../../../react-kit/util/Functions');
var ValidateUtil = require('./ValidateUtil');

const CompanyUtil = {

    reverseFundings(list){
        if (list == null) return [];
        var newList = list.sort(function (a, b) {
            return a.funding.fundingDate < b.funding.fundingDate ? 1 : -1;
        });

        return newList;
    },

    reverseFootprints(list){
        if (list == null) return [];
        var newList = list.sort(function (a, b) {
            return a.footDate < b.footDate ? 1 : -1;
        });

        return newList;
    },

    sortDevelop(footprints, fundings){
        var sortList = [];

        for (var i in footprints) {
            var item = footprints[i];
            item.date = footprints[i].footDate;
            item.type = 'footprint';

            if (item.date != null) {
                item.date = item.date.substring(0, 7);
            }
            sortList.push(item);
        }

        for (var i in fundings) {
            var item = fundings[i]
            item.date = fundings[i].funding.fundingDate;
            item.type = 'funding';

            if (item.date != null) {
                item.date = item.date.substring(0, 7);
            }
            sortList.push(item);
        }

        var sortList = sortList.sort(function (a, b) {
            return a.date < b.date ? 1 : -1;
        });

        return sortList;
    },


    getSubList(list, len, flag){
        var showAll = false;
        if (list.length > len) {
            showAll = true;
            if (!flag) {
                var shortList = [];
                for (var i = 0; i < len; i++) {
                    shortList.push(list[i])
                }
                list = shortList;
            }
        }

        //return {list:list, show: showAll};
        return list;
    },


    getParentSector(sectors){
        if (sectors.length == 0) return {};
        for (var i in sectors) {
            if (sectors[i].level == 1) return sectors[i];
        }
    },

    getSubSector(sectors){
        if (sectors.length < 2) return {};
        for (var i in sectors) {
            if (sectors[i].level == 2) return sectors[i];
        }
    },

    checkCompanyDiff(update, old){
        if (update != old)
            return true;
        return false;
    },

    checkFootprintDiff(update, list){
        for (var i in list) {
            if (update.id == list[i].id) {
                if (update.footDate != list[i].footDate) return true;
                if (update.description != list[i].description) return true;
            }
        }
        return false;
    },

    checkFundingDiff(update, list){
        for (var i in list) {
            if (update.funding.id == list[i].funding.id) {
                if (JSON.stringify(update) != JSON.stringify(list[i]))
                    return true;
            }
        }
        return false;
    },

    checkSectorDiff(update, old){
        if (update == null) return false;
        if (old == null) {
            if (update.id > 0) return true;
        }

        if (update.id != old.id)
            return true;
        return false;
    },


    initSector(){

    },

    initTag(){
        var tag = {
            id: null,
            companyId: null,
            tagId: null
        }
        return tag;
    },

    initFunding(){

        var funding = {
            id: null,
            companyId: null,
            preMoney: null,
            postMoney: null,
            investment: null,
            round: null,
            roundDesc: null,
            currency: null,
            precise: null,
            fundingDate: null,
            fundingType: null
        };

        var firList = [];

        var fundingVO = {
            funding: funding,
            firList: firList
        };

        return fundingVO;
    },

    initFIR(){
        var fir = {
            id: null,
            fundingId: null,
            investorId: null,
            currency: null,
            investment: null,
            precise: null
        };

        var investor = {
            id: null,
            name: null
        };
        var firVO = {
            fir: fir,
            investor: investor
        };

        return firVO;
    },


    initFootprint(){
        var footprint = {
            id: null,
            companyId: null,
            footDate: null,
            description: null
        }

        return footprint;
    },

    initDocument(){
        var document = {
            id: null,
            companyId: null,
            name: null,
            description: null,
            link: null,
            type: null
        }

        return document;
    },


    headCountSelect(){
        headCountSelect = [
            {name: '请选择', value: 0},
            {name: '1~15', value: 1},
            {name: '15~50', value: 2},
            {name: '50~150', value: 3},
            {name: '150~500', value: 4},
            {name: '500~2000', value: 5},
            {name: '2000以上', value: 6}
        ];

        return headCountSelect;
    },

    getHeadCount(value){
        var result;
        switch (Number(value)) {
            case 1:
                result = 1;
                break;
            case 15:
                result = 2;
                break;
            case 50:
                result = 3;
                break;
            case 150:
                result = 4;
                break;
            case 500:
                result = 5;
                break;
            case 2000:
                result = 6;
                break;
        }
        return result;
    },

    getHeadCounts(value){
        var headCountMin;
        var headCountMax;
        switch (Number(value)) {
            case 1:
                headCountMin = 1;
                headCountMax = 15;
                break;
            case 2:
                headCountMin = 15;
                headCountMax = 50;
                break;
            case 3:
                headCountMin = 50;
                headCountMax = 150;
                break;
            case 4:
                headCountMin = 150;
                headCountMax = 500;
                break;
            case 5:
                headCountMin = 500;
                headCountMax = 2000;
                break;
            case 6:
                headCountMin = 2000;
                break;
        }


        return {min: headCountMin, max: headCountMax};
    },

    getSectorName(value, list){
        for (var i in list) {
            if (list[i].id == value) {
                return list[i].sectorName;
            }
        }
    },

    /*************  add new *****************/

        addFootprint(store){
        var footprint = store.addFootprint;
        //if(!this.checkFootprint(footprint)) return store;

        store.addFootprint.companyId = store.companyId;
        store.newFootprints.push(footprint);
        store.addFootprint = this.initFootprint();

        return store;
    },

    checkFootprint(footprint){
        if (Functions.isNull(footprint.description)) return false;
    },

    addFunding(){

    },


    /*************  update ************/

        checkListChange(update, old){
        if (JSON.stringify(update) == JSON.stringify(old)) return false;
        return true;
    },

    updateCompany(store){
        var update = store.updateCompany;
        var old = store.company;

        if (!this.checkListChange(update, old)) return;

        update = this.parseUpdateFundingDB(update);

        var payload = {payload: {update: update}};
        var url = "/api/company/update";
        var callback = function (result) {
            console.log(result);
        };

        Http.ajax(payload, url, callback);
    },


    updateSector(store){
        var updateParentSector = store.updateParentSector;
        var updateSubSector = store.updateSubSector;
        var parentSector = store.parentSector;
        var subSector = store.subSector;
        var companyId = store.companyId;

        if (Functions.isEmptyObject(updateParentSector)) return;
        var sectorIds = [];
        var updateParentId = null;
        var updateSubId = null;
        updateParentId = updateParentSector.id;
        sectorIds.push(updateParentId);

        if (!Functions.isEmptyObject(updateSubSector)) {
            updateSubId = updateSubSector.id;
            sectorIds.push(updateSubId);
        }

        var parentId = null;
        var subId = null;
        if (!Functions.isEmptyObject(parentSector)) {
            parentId = parentSector.id;
        }
        if (!Functions.isEmptyObject(subSector)) {
            subId = subSector.id;
        }

        if (updateParentId == parentId && updateSubId == subId) return;

        this.updateSectorDB(sectorIds, companyId)
    },

    updateSectorDB(sectorIds, companyId){
        var payload = {payload: {sectorIds: sectorIds, companyId: companyId}};
        var url = "/api/company/sector/update";
        var callback = function (result) {
            console.log(result);
        };

        Http.ajax(payload, url, callback);
    },


    /********* tag *********/

        updateTags(store){
        var tags = store.tags;
        var updateTags = store.updateTags;
        var newTags = store.newTags;
        var deleteIds = store.deleteTags;
        var companyId = store.companyId;


        this.addTagDB(newTags, companyId);
        this.deleteTagDB(deleteIds, companyId);
    },

    addTagDB(newTags, companyId){
        if (newTags.length == 0) return;

        var ids = [];
        for (var i in newTags) {
            ids.push(Number(newTags[i].id));
        }
        var payload = {payload: {ids: ids, companyId: companyId}};
        var url = "/api/company/tag/add";
        var callback = function (result) {
            console.log(result);
        };

        Http.ajax(payload, url, callback);
    },

    deleteTagDB(deleteIds, companyId){
        if (deleteIds.length == 0) return;

        var payload = {payload: {ids: deleteIds, companyId: companyId}};
        var url = "/api/company/tag/delete";
        var callback = function (result) {
            console.log(result);
        };

        Http.ajax(payload, url, callback);
    },


    /********* file *********/

        updateDocuments(store){
        var newDocuments = store.newDocuments;
        var deleteIds = store.deleteDocuments;
        var companyId = store.companyId;

        this.addDocumentDB(newDocuments);
        this.deleteDocumentDB(deleteIds, companyId);
    },

    addDocumentDB(files){
        if (files.length == 0) return;
        var payload = {payload: {documents: files}};
        var url = "/api/company/document/add";
        var callback = function (result) {
            console.log(result);
        };

        Http.ajax(payload, url, callback);
    },

    deleteDocumentDB(deleteIds, companyId){
        if (deleteIds.length == 0) return;

        var payload = {payload: {ids: deleteIds, companyId: companyId}};
        var url = "/api/company/document/delete";
        var callback = function (result) {
            console.log(result);
        };

        Http.ajax(payload, url, callback);
    },

    /********* footprint *********/

        updateFootprints(store){
        var newFootprints = store.newFootprints;
        var updateFootprints = store.updateFootprints;
        var oldFootprints = store.footprints;
        var deleteIds = store.deleteFootprints;

        this.addFootprintDB(newFootprints);
        this.updateFootprintDB(updateFootprints, oldFootprints);
        this.deleteFootprintDB(deleteIds);
    },

    addFootprintDB(newFootprints){
        if (newFootprints.length == 0) return;

        var payload = {payload: {footprints: newFootprints}};
        var url = "/api/company/footprint/add";
        var callback = function (result) {
            console.log(result);
        };

        Http.ajax(payload, url, callback);
    },

    updateFootprintDB(update, old){
        if (!this.checkListChange(update, old)) return;

        var updateList = [];
        for (var i in update) {
            var flag = false;
            for (var k in old) {
                if (update[i].id == old[k].id) {
                    if (update[i].footDate != old[k].footDate) flag = true;
                    if (update[i].description != old[k].description) flag = true;
                }
            }

            if (flag) updateList.push(update[i]);
        }

        var payload = {payload: {footprints: updateList}};
        var url = "/api/company/footprint/update";
        var callback = function (result) {
            console.log(result);
        };

        Http.ajax(payload, url, callback);

    },


    deleteFootprintDB(deleteIds){
        if (deleteIds.length == 0) return;

        var payload = {payload: {ids: deleteIds}};
        var url = "/api/company/footprint/delete";
        var callback = function (result) {
            console.log(result);
        };

        Http.ajax(payload, url, callback);
    },

    /********* funding *********/
        updateFundings(store){
        var updateFundings = store.updateFundings;
        var fundings = store.fundings;
        if (updateFundings.length == 0 && fundings.length == 0) {
            return;
        } else if (updateFundings.length > 0 && fundings.length == 0) {
            //全部为新增
            this.toAddFundingAndFir(updateFundings);
        } else if (updateFundings.length == 0 && fundings.length > 0) {
            //全部删除
            this.toDeleteFundings(store.deleteFundings);
        } else {
            //有新增，也有删除，最复杂的情况
            //此处只是先处理了新增和修改
            for (var k in updateFundings) {
                var fundingVO = updateFundings[k];
                this.checkFundingAndInvestorDiff(fundingVO, fundings);
            }
            //删除的funding
            this.toDeleteFundings(store.deleteFundings);

        }
    },

    checkFundingAndInvestorDiff(fundingVO, fundings){
        //先看此条记录在fundings中是否促在
        var funding = fundingVO.funding;
        var firList = fundingVO.firList;
        var fundingId = funding.id;
        if (fundingId) {
            for (var k in fundings) {
                //JSON.stringify
                if (fundingId == fundings[k].funding.id) {
                    this.findDiff(fundingVO, fundings[k]);
                    break;
                }
            }
        }
        else {
            //没有id，表示该条记录是新增的
            this.addFundingAndFirList(funding, firList);
        }
    },

    findDiff(fundingVO, orgFundingVO){
        //没有任何改变
        if (JSON.stringify(fundingVO) == JSON.stringify(orgFundingVO)) return;

        var funding = fundingVO.funding;
        var orgFunding = orgFundingVO.funding;
        var firList = fundingVO.firList;
        var orgFirList = orgFundingVO.firList;

        if (JSON.stringify(funding) != JSON.stringify(orgFunding)) {
            //update funding
            this.toUpdateFunding(funding);
        }
        if (JSON.stringify(firList) != JSON.stringify(orgFirList)) {
            //遍历这这两个list，找出增加的和减少的fir
            var result = this.findFIRIncAndDesc(firList, orgFirList);
            this.addFirs(result.addList);
            this.deleteFirs(result.descList);
        }
    },

    findFIRIncAndDesc(firList, orgFirList){
        var desc;
        var descList = [];
        var add;
        var addList = [];

        var orgId;
        var id;
        //fir被全部删除
        if ((firList == null || firList.length == 0) && (orgFirList != null && orgFirList.length > 0)) {
            for (var h in orgFirList) {
                descList.push(orgFirList[h].fir);
            }
            return {
                descList: descList,
                addList: []
            }
        }
        //全部为新增
        if ((orgFirList == null || orgFirList.length == 0) && (firList != null && firList.length > 0)) {
            for (var f in firList) {
                addList.push(firList[f].fir);
            }
            return {
                descList: [],
                addList: firList
            }
        }
        //没有增加，也没有减少
        if ((orgFirList == null || orgFirList.length == 0) && (firList == null || firList.length == 0)) {
            return {
                descList: [],
                addList: []
            }
        }
        //先找出其中减少的fir
        for (var k in orgFirList) {
            desc = true;
            orgId = orgFirList[k].fir.id;
            for (var i in firList) {
                if (orgId == firList[i].fir.id) {
                    desc = false;
                    break;
                }
            }
            if (desc) {
                descList.push(orgFirList[k].fir);
            }
        }

        for (var m in firList) {
            add = true;
            id = firList[m].fir.id
            for (var j in orgFirList) {
                if (id == orgFirList[j].fir.id) {
                    add = false;
                    break;
                }
            }
            if (add) {
                addList.push(firList[m].fir);
            }
        }
        return {
            descList: descList,
            addList: addList
        }
    },

    toUpdateFunding(funding){
        var payload = {payload: {funding: funding}};
        var url = "/api/company/funding/update";
        var callback = function (result) {
            if (result.code == 0) {
            }
        };
        Http.ajax(payload, url, callback);
    },

    addFirs(addList){
        if (addList.length == 0)return;
        var payload = {payload: {addList: addList}};
        var url = "/api/company/funding/fir/add";
        var callback = function (result) {
            if (result.code == 0) {
            }
        };
        Http.ajax(payload, url, callback);
    },

    deleteFirs(descList){
        if (descList.length == 0)return;
        var payload = {payload: {descList: descList}};
        var url = "/api/company/funding/fir/delete";
        var callback = function (result) {
            if (result.code == 0) {
            }
        };
        Http.ajax(payload, url, callback);
    },


    toDeleteFundings(list){
        if (list.length == 0) return;
        var payload = {payload: {ids: list}};
        var url = "/api/company/funding/delete";
        var callback = function (result) {
            if (result.code == 0) {
            }
        };
        Http.ajax(payload, url, callback);
    },

    toAddFundingAndFir(list){
        if (list.length == 0) return;
        for (var i in list) {
            var fundingVO = list[i];
            var funding = fundingVO.funding;
            var firList = fundingVO.firList;
            this.addFundingAndFirList(funding, firList);
        }
    },

    addFundingAndFirList(funding, firList){
        var payload = {payload: {funding: funding, firList: firList}};
        var url = "/api/company/funding/new/funding";
        var callback = function (result) {
            if (result.code == 0) {
                funding = result.funding;
            }
        };
        Http.ajax(payload, url, callback);
    },

    updateFundingAndInvestor(store, type){
        var updateFundings = store.updateFundings;
        var funding;
        if (type == "addFunding") {
            store.addFunding.funding.companyId = store.companyId;
            updateFundings.push(store.addFunding);

        } else {
            funding = store.selectedFunding.funding;
            for (var k in updateFundings) {
                if (updateFundings[k].funding.id == funding.id) {
                    updateFundings[k] = store.selectedFunding;
                }
            }
        }
    },

    deleteFIR(fir, store, type){
        var location;
        var firList;
        if (type == 'addFunding') {
            firList = store.addFunding.firList;
            for (var k in firList) {
                if (firList[k].fir.investorId == fir.investorId) {
                    location = k;
                    break;
                }
            }
        }
        else {
            firList = store.selectedFunding.firList;
            for (var i in firList) {
                if (firList[i].fir.id == fir.id) {
                    location = i;
                    break;
                }
            }
        }
        if (location) {
            firList.splice(location, 1);
        }
    },

    /*********** validate **********/
        validateFromDemoday(store){
        var company = store.updateCompany;
        var parentSector = store.updateParentSector;
        var subSector = store.updateSubSector;

        if (Functions.isNull(company.name)) {
            $('#company-warn > .warn-body > .warn-content').html('请完善产品名称');
            $('#company-warn').show();
            return false;
        }

        if (Functions.isNull(company.brief)) {
            $('#company-warn > .warn-body > .warn-content').html('请完善一句话简介');
            $('#company-warn').show();
            return false;
        }

        if (Functions.isNull(company.locationId) ||
            Functions.isNull(company.location)) {
            $('#company-warn > .warn-body > .warn-content').html('请完善公司地址');
            $('#company-warn').show();
            return false;
        }

        //if(!ValidateUtil.validateDate(company.establishDate)){
        //    $('#company-warn > .warn-body > .warn-content').html('请完善建立时间');
        //    $('#company-warn').show();
        //    return false;
        //}

        if (Functions.isNull(company.description)) {
            $('#company-warn > .warn-body > .warn-content').html('请完善公司简介');
            $('#company-warn').show();
            return false;
        }

        if (Functions.isEmptyObject(parentSector) ||
            Functions.isEmptyObject(subSector)) {
            $('#company-warn > .warn-body > .warn-content').html('请完善行业信息');
            $('#company-warn').show();
            return false;
        }


        if (company.round == null ||
            company.round == 0 ||
            company.investment == null ||
            company.investment == 0 ||
            company.preMoney == null ||
            company.preMoney == 0 ||
            company.postMoney == null ||
            company.postMoney == 0 ||
            company.shareRatio == null ||
            company.shareRatio == 0) {

            $('#company-warn > .warn-body > .warn-content').html('请完善融资状态');
            $('#company-warn').show();
            return false;
        }

        if (store.updateDocuments.length == 0 && store.newDocuments.length == 0) {
            $('#company-warn > .warn-body > .warn-content').html('请上传BP');
            $('#company-warn').show();
            return false;
        }

        return true;
    },


    /************ parse **************/
        parseRoundFunding(currency, money){
        money = '' + money;
        money = this.parsePreciseIsY(money)
        if (currency == 3010) {
            currency = ' $ ';
        } else if (currency == 3020) {
            currency = '￥';
        } else {
            currency = '';
        }

        if (money == 0 || money == '') {
            money = 'N/A';
            currency = '';
        }


        return currency + money;
    },


    parseFunding(funding){
        var fundingInfo;
        var precise = funding.precise;
        var currency = funding.currency;
        var investment = '' + funding.investment;
        if (investment == 0) {
            return '金额未知';
        }

        if (currency == 3010) {
            currency = ' $ ';
        } else if (currency == 3020) {
            currency = '￥';
        } else {
            currency = '';
        }

        if (precise == 'N') {
            investment = this.parsePreciseIsN(investment)
        } else {
            investment = this.parsePreciseIsY(investment);
        }

        fundingInfo = currency + '' + investment + '';
        return fundingInfo;
    },

    parsePreciseIsN(investment){
        switch (investment.length) {
            case 5:
                return '数万';
            case 6:
                return '数十万';
            case 7:
                return '数百万';
            case 8:
                return '数千万';
            case 9:
                return '数亿';
            case 10:
                return '数十亿';
        }

    },

    parsePreciseIsY(investment){
        var flag = this.parseMoney(investment);
        if (!flag)
            return Functions.parseNumber(investment);

        var money = investment.substring(0, 1);

        switch (investment.length) {
            case 5:
                return money + '万';
            case 6:
                return money + '0万';
            case 7:
                return money + '00万';
            case 8:
                return money + '000万';
            case 9:
                return money + '亿';
            case 10:
                return money + '0亿';
        }
    },

    parseMoney(money){
        //console.log(money)
        if (money.length <= 4) {
            return false;
        }
        for (var i in money) {
            if (i > 0) {
                if (money[i] != 0) {
                    return false;
                }
            }
        }
        return true;
    },

    parseUpdateFunding(company){
        var investment = company.investment;
        var preMoney = company.preMoney;
        var postMoney = company.postMoney;
        if (investment != null) {
            company.investment = investment / 10000;
        }

        if (preMoney != null) {
            company.preMoney = preMoney / 10000;
        }

        if (postMoney != null) {
            company.postMoney = postMoney / 10000;
        }

        return company;
    },

    parseUpdateFundingDB(company){
        var investment = company.investment;
        var preMoney = company.preMoney;
        var postMoney = company.postMoney;
        if (investment != null) {
            company.investment = investment * 10000;
        }

        if (preMoney != null) {
            company.preMoney = preMoney * 10000;
        }

        if (postMoney != null) {
            company.postMoney = postMoney * 10000;
        }

        return company;
    },


    yearSelect(){
        var date = new Date().getFullYear();
        var dateSelect = [];
        dateSelect.push({value: 0, name: '请选择创立年份'});
        for (var i = 0; i < 15; i++) {
            var ele = {value: date, name: date + '年'};
            dateSelect.push(ele);
            date = date - 1;
        }
        return dateSelect;
    },


    monthSelect(){
        var dateSelect = [];
        dateSelect.push({value: 0, name: '请选择月份'});
        for (var i = 1; i < 13; i++) {
            var month = i;
            if (i < 10) {
                month = 0 + '' + i;
            }
            var ele = {value: month, name: i + '月'};
            dateSelect.push(ele);
        }
        return dateSelect;
    }

};


module.exports = CompanyUtil;