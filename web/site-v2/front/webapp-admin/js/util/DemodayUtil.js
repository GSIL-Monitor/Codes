var Functions = require('../../../react-kit/util/Functions');
const DemodayUtil = {
    createBlankDemoday() {
        return {
            name: null,
            submitEndDate: null,
            preScoreStartDate: null,
            preScoreEndDate: null,
            connectStartDate: null,
            connectEndDate: null,
            holdStartDate: null,
            holdEndDate: null
        };
    },

    getSelectedIds(ids){
        var list = [];
        for (var i in ids) {
            if (ids[i].selected) {
                list.push(ids[i].id);
            }
        }
        return list;
    },

    dateToString(date){
        var month = date.getMonth() + 1;
        var day = date.getDate();
        if (month < 10) {
            month = '0' + month;
        }
        if (day < 10) {
            day = '0' + day;
        }

        return date.getFullYear() + "-" + month + "-" + day;
    },

    parseDemodayOrgs(orgList){
        var orgs = {joinOrgs: [], rejectOrgs: []};
        for (var i in orgList) {
            if (orgList[i].status === 28030) {
                orgs.joinOrgs.push(orgList[i]);
            }
            else {
                orgs.rejectOrgs.push(orgList[i]);
            }
        }
        return orgs;
    },
    /**demoday状态*/
    status: [
        {name: '项目提交中', value: 26000},
        {name: '项目提交结束', value: 26005},
        {name: '初筛选', value: 26010},
        {name: '筛选结束', value: 26020},
        {name: '通知团队', value: 26024},
        {name: '通知团队结束', value: 26027},
        {name: '进行中', value: 26030},
        {name: '已结束', value: 26040}
    ],
    /**joinstatus*/
    joinStatus: [
        {name: '联络中', value: 28010},
        {name: '不参加', value: 28020},
        {name: '参加', value: 28030},
        {name: '申请中', value: 28040},
        {name: '申请通过', value: 28050}
    ],
    /**demo day公司打分状态*/
    scoringStatus: [
        {name: '初筛选中', value: 27010},
        {name: '初筛选通过', value: 27020},
        {name: '初筛选失败', value: 27030},
        {name: '打分中', value: 27040},
        {name: '打分结束', value: 27050}
    ],
    orgGrade:[
        {name: '部分功能', value: 33020},
        {name: '全功能', value: 33010},
    ],
    getScoreStatus(status){
        var name;
        switch (status) {
            case 27010:name = '初筛选中';break;
            case 27020:name = '初筛选通过';break;
            case 27030:name = '初筛选失败';break;
            case 27040:name = '打分中';break;
            case 27050:name = '打分结束';break;
        }
        return name;
    },

    getJoinStatus(status){
        var name;
        switch (status) {
            case 28010:name = '联络中';break;
            case 28020:name = '不参加';break;
            case 28030:name = '参加';break;
            case 28040:name = '申请中';break;
            case 28050:name = '申请通过';break;
        }
        return name;
    },

    compare(newDemoay, oldDemoday){
        if (newDemoay.name != oldDemoday.name) return true;
        if (newDemoay.submitEndDate != oldDemoday.submitEndDate)return true;
        if (newDemoay.preScoreStartDate != oldDemoday.preScoreStartDate)return true;
        if (newDemoay.preScoreEndDate != oldDemoday.preScoreEndDate)return true;
        if (newDemoay.connectStartDate != oldDemoday.connectStartDate)return true;
        if (newDemoay.connectEndDate != oldDemoday.connectEndDate)return true;
        if (newDemoay.holdStartDate != oldDemoday.holdStartDate)return true;
        if (newDemoay.holdEndDate != oldDemoday.holdEndDate)return true;
        if (newDemoay.status != oldDemoday.status)return true;
        return false;
    },

    removeDemodayOrg(joinOrgs, orgId, rejectOrgs){

        if (null == rejectOrgs) {
            rejectOrgs = [];
        }
        for (var i in joinOrgs) {
            if (joinOrgs[i].orgId == orgId) {
                joinOrgs[i].status = 28020;
                rejectOrgs.push(joinOrgs[i]);
            }
        }
        var tempOrgs = Functions.clone(joinOrgs);
        for (var k in joinOrgs) {
            if (joinOrgs[k].orgId == orgId) {
                tempOrgs.splice(k, 1);
            }
        }
        return tempOrgs;
    },

    addDemodayOrgs(joinOrgs, orgIds, rejectOrgs){

        if (null == joinOrgs) {
            joinOrgs = [];
        }
        for (var i in orgIds) {
            for (var k in rejectOrgs) {
                if (orgIds[i] == rejectOrgs[k].orgId) {
                    rejectOrgs[k].status = 28030;
                    joinOrgs.push(rejectOrgs[k]);
                }
            }
        }
        var tempOrgs = Functions.clone(rejectOrgs);
        for (var m in orgIds) {
            for (var n in rejectOrgs) {
                if (orgIds[m] == rejectOrgs[n].orgId) {
                    tempOrgs.splice(n, 1);
                }
            }

        }
        return tempOrgs;
    },

    orgSelected(addOrgIds){
        if (addOrgIds.length == 0) return false;
        for (var i in addOrgIds) {
            if (addOrgIds[i].selected) return true;
        }
        return false;
    },

    updateStatus(companies, name, value, code){
        for (var i in companies) {
            if (companies[i].code == code) {
                companies[i][name] = Number(value);
            }
        }
        return companies;
    },

    getDemodayStatus(status){
        switch (Number(status)) {
            case 26000:return '项目提交中';
            case 26005:return '项目提交结束';
            case 26010:return '初筛选';
            case 26020:return '筛选结束';
            case 26024:return '通知团队';
            case 26027:return '通知团队结束';
            case 26030:return '进行中';
            case 26040:return '完成';
        }
    },

    getDateList(demoday){
        var dateList = [];
        dateList.push({name:"submitEndDate",status: 26005, nodeName: '项目提交截止日期',nodeDate:Functions.dateFormat2(demoday.submitEndDate)});
        dateList.push({name:"preScoreStartDate",status: 26010, nodeName: '初筛选日期', nodeDate: Functions.dateFormat2(demoday.preScoreStartDate)});
        dateList.push({name:"preScoreEndDate",status: 26020, nodeName: '筛选截止日期', nodeDate: Functions.dateFormat2(demoday.preScoreEndDate)});
        dateList.push({name:"connectStartDate",status: 26024, nodeName: '通知团队日期', nodeDate: Functions.dateFormat2(demoday.connectStartDate)});
        dateList.push({name:"connectEndDate",status: 26027, nodeName: '通知团队结束日期', nodeDate: Functions.dateFormat2(demoday.connectEndDate)});
        dateList.push({name:"holdStartDate",status: 26030, nodeName: '举行日期', nodeDate:  Functions.dateFormat2(demoday.holdStartDate)});
        dateList.push({name:"holdEndDate",status: 26040, nodeName: '结束日期', nodeDate:  Functions.dateFormat2(demoday.holdEndDate)});
        return dateList;
    },

    setPreScoreResult(preScores, id, status){
        for (var i in preScores) {
            if (preScores[i].demodayCompanyId === id) {
                preScores[i].scoringStatus = status;
            }
        }
        return preScores;
    },

    setPreScoreResults(preScores,ids,status){
        for(var i in ids){
            for(var k in preScores){
                if (preScores[k].demodayCompanyId === ids[i]) {
                    preScores[k].scoringStatus = status;
                }
            }
        }
        return preScores;
    },
    parserDemoday(demoday){
        var  submitEndDate= new Date(demoday.submitEndDate);
        demoday.submitEndDate= submitEndDate.getTime();

        var  preScoreStartDate= new Date(demoday.preScoreStartDate);
        demoday.preScoreStartDate= preScoreStartDate.getTime();

        var  preScoreEndDate= new Date(demoday.preScoreEndDate);
        demoday.preScoreEndDate= preScoreEndDate.getTime();

        var  connectStartDate= new Date(demoday.connectStartDate);
        demoday.connectStartDate= connectStartDate.getTime();

        var connectEndDate = new Date(demoday.connectEndDate);
        demoday.connectEndDate= connectEndDate.getTime();

        var  holdStartDate= new Date(demoday.holdStartDate);
        demoday.holdStartDate= holdStartDate.getTime();

        var  holdEndDate= new Date(demoday.holdEndDate);
        demoday.holdEndDate= holdEndDate.getTime();

        return demoday;
    }
};

module.exports = DemodayUtil;

