var $ = require('jquery');
var CreateCompanyActions = require('../action/CreateCompanyActions');

const CreateCompanyUtil = {

    createBlankCompany() {
        return {
            name: "",
            fullName: "",
            brief: "",
            description: "",
            round: "",
            currency: 3020,
            preMoney: "",
            postMoney: "",
            investment: "",
            locationId: null,
            establishDate: "",
            shareRatio: "",
            headCountMax: null,
            headCountMin: null

        };
    },

    createBlankMember() {
        return {
            name: "",
            education: "",
            work: "",
            phone: ""
        }
    },
    /**
     * 融资阶段
     * */
    round: [
        {name: '请选择阶段', value: ""},
        {name: '未融资', value: 0},
        {name: '天使轮', value: 1010},
        {name: 'pre-A', value: 1020},
        {name: 'A轮', value: 1030},
        {name: 'A+轮', value: 1031},
        {name: 'B轮', value: 1040},
        {name: 'C轮', value: 1050},
        {name: 'D轮以上', value: 1060},
        {name: 'IPO', value: 1110},
        {name: '被收购', value: 1120},

    ],
    /**货币种类*/
    currency: [
        {name: '万人民币CNY', value: 3020},
        {name: '万美元USD', value: 3010},
    ],
    /**
     * 1-6代表规模档次
     * */
    teamSize: [
        {name: '请选择规模', value: 0},
        {name: '1~15', value: 1},
        {name: '15~50', value: 2},
        {name: '50~150', value: 3},
        {name: '150~500', value: 4},
        {name: '500~2000', value: 5},
        {name: '2000以上', value: 6}

    ],

    getMemberNums(teamSize){
        var memberNum = {
            headCountMin: null,
            headCountMax: null
        }
        switch (Number(teamSize)) {
            case 1:
                memberNum.headCountMax = 15;
                memberNum.headCountMin = 1;
                break;
            case 2:
                memberNum.headCountMax = 50;
                memberNum.headCountMin = 15;
                break;
            case 3:
                memberNum.headCountMax = 150;
                memberNum.headCountMin = 50;
                break;
            case 4:
                memberNum.headCountMax = 500;
                memberNum.headCountMin = 150;
                break;
            case 5:
                memberNum.headCountMax = 2000;
                memberNum.headCountMin = 500;
                break;
            case 6:
                memberNum.headCountMin = 2000;
                break;
        }
        return memberNum;
    },

    getTagIds(tags){
        var ids = [];
        for (var k in tags) {
            ids.push(Number(tags[k].id))
        }
        return ids;
    },

    getProductList(productList){
        var list = [];
        for (var k in productList) {
            if (productList[k].selected) {
                var item = {name: null, type: null}
                item.name = productList[k].name;
                item.type = productList[k].type;
                list.push(item);
            }
        }
        return list;
    },

    sources: [
        {name: '请选择来源', value: 0},
        {name: 'FA:以太', value: 13100},
        {name: 'FA:华兴alpha', value: 13101},
        {name: 'FA:小饭桌', value: 13102},
        {name: 'FA:36Kr-新军资本', value: 13103},
        {name: 'FA:方创', value: 13104},
        {name: '京东股权众筹', value: 13200},
        {name: '36Kr-股权众筹', value: 13201}
    ]
}

module.exports = CreateCompanyUtil;