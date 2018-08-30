var $ = require('jquery');


var Functions = {

    clone(obj) {
        return JSON.parse(JSON.stringify(obj));
    },

    getRoundName(round){
        var roundName;
        switch (Number(round)) {
            case 0:
                roundName = 'N/A';
                break;
            case 1010:
                roundName = '天使轮';
                break;
            case 1020:
                roundName = 'Pre-A轮';
                break;
            case 1030:
                roundName = 'A轮';
                break;
            case 1040:
                roundName = 'B轮';
                break;
            case 1050:
                roundName = 'C轮';
                break;
            case 1060:
                roundName = 'D轮';
                break;
            case 1070:
                roundName = 'E轮';
                break;
            case 1080:
                roundName = 'F轮';
                break;
            case 1090:
                roundName = '后期阶段';
                break;
            case 1100:
                roundName = 'Pre-IPO';
                break;
            case 1110:
                roundName = 'IPO';
                break;
            case 1120:
                roundName = '被收购';
                break;
            default :
                roundName ='';
                break;

            }

        return roundName;
    },


    /****************** select *******************/

    roundSelect(){
        var roundSelect = [
            {value: 1010, name: '天使轮'},
            {value: 1020, name: 'Pre-A轮'},
            {value: 1030, name: 'A轮'},
            {value: 1040, name: 'B轮'},
            {value: 1050, name: 'C轮'},
            {value: 1060, name: 'D轮'},
            {value: 1070, name: 'E轮'},
            {value: 1080, name: 'F轮'},
            {value: 1090, name: '后期阶段'},
            {value: 1100, name: 'Pre-IPO'},
            {value: 1110, name: 'IPO'},
            {value: 1120, name: '被收购'}
        ];

        return roundSelect;
    },

    currencySelect(){
        var currencySelect = [
            {value: 3010, name: '美元'},
            {value: 3020, name: '人民币'}
            //{value: 3030, name: 'SGD'}
        ];

        return currencySelect;
    },

    preciseSelect(){
        var preciseSelect = [
            {value: 'N', name:'不确定'},
            {value: 'Y', name:'确定'}
        ];

        return preciseSelect;
    },

    memberTypeSelect(){
        var memberTypeSelect = [
            {value: 0, name:'未知'},
            {value: 5010, name:'创始人'},
            {value: 5020, name:'核心成员'},
            {value: 5030, name:'普通成员'},
            {value: 5040, name:'过往成员'}
        ];
        return memberTypeSelect;
    },


    fundingTypeSelect(){
        var fundingTypeSelect = [
            {value: 8030, name:'已完成'},
            {value: 8020, name:'需要融资'},
            {value: 8010, name:'不需要融资'},
        ];
        return fundingTypeSelect;
    },


    sortSelect(){
        var sortSelect = [
            {value: 1, name:'匹配度'},
            {value: 2, name:'轮次'},
            {value: 3, name:'建立时间'},
            {value: 4, name:'地点'},
            {value: 5, name:'投资方'},
        ];
        return sortSelect;
    },


    investorTypeSelect(){
        var investorTypeSelect = [
            {value: 10020, name:'公司'},
            {value: 10010, name:'个人'},
        ];
        return investorTypeSelect;
    },


    /**************  useful list ************/
    locationUseful(){
        var data = [
            {name: '北京', value: 1},
            {name: '上海', value: 2},
            {name: '杭州', value: 360},
            {name: '南京', value: 185},
            {name: '深圳', value: 63},
            {name: '广州', value: 52},
            {name: '成都', value: 296},
            {name: '苏州', value: 197},
            {name: '厦门', value: 32}
        ];

        return data;
    },

    investorUseful(){
        var data = [
            {name: '戈壁', value: 149},
            {name: 'IDG', value: 109},
            {name: '红杉', value: 114},
            {name: '真格', value: 122},
            {name: '经纬', value: 125}
        ];

        return data;
    }

};











module.exports = Functions;




