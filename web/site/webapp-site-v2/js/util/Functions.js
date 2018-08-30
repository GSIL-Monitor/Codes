var $ = require('jquery');


var Functions = {

    clone(obj) {
        return JSON.parse(JSON.stringify(obj));
    },

    isEmptyObject(obj){
        for(var n in obj){return false}
        return true;
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

    sortSelect(){
        var sortSelect = [
            {value: 1, name:'匹配度'},
            {value: 2, name:'轮次'},
            {value: 3, name:'建立时间'},
            {value: 4, name:'地点'},
            {value: 5, name:'投资方'},
        ];
        return sortSelect;
    }
};


module.exports = Functions;




