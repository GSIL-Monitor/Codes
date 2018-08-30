var $ = require('jquery');

Date.prototype.format = function(fmt)
{
    var o = {
        "M+" : this.getMonth()+1,                 //月份
        "d+" : this.getDate(),                    //日
        "h+" : this.getHours(),                   //小时
        "m+" : this.getMinutes(),                 //分
        "s+" : this.getSeconds(),                 //秒
        "q+" : Math.floor((this.getMonth()+3)/3), //季度
        "S"  : this.getMilliseconds()             //毫秒
    };
    if(/(y+)/.test(fmt))
        fmt=fmt.replace(RegExp.$1, (this.getFullYear()+"").substr(4 - RegExp.$1.length));
    for(var k in o)
        if(new RegExp("("+ k +")").test(fmt))
            fmt = fmt.replace(RegExp.$1, (RegExp.$1.length==1) ? (o[k]) : (("00"+ o[k]).substr((""+ o[k]).length)));
    return fmt;
};

var Functions = {

    clone(obj) {
        return JSON.parse(JSON.stringify(obj));
    },

    isEmptyObject(obj){
        if(obj == null) return true;
        for(var n in obj){return false}
        return true;
    },

    isNull(value){
        if(value == null || value == "" || value == undefined){
            return true;
        }
        else if((value+"").trim() == null){
            return true;
        }
        return false
    },

    checkExist(name, obj){
        for(var k in obj){
            if(k == name){
                if(obj[k] == null)
                    return false;
                if(obj[k].length > 0)
                    return true;
            }
        }
        return false;
    },

    checkContent(content){
        if(null==content||""==content){
            return false;
        }
        else return true;
    },

    parseCount(value){
        value = value+"";
        if(value == null) return null;
        var len = value.length;
        if(len > 9){
            value = value.substring(0, len-9)+','+ value.substring(len-9, len-6)+','
                +value.substring(len-6, len-3)+','+ value.substring(len-3)
        }
        else if(len > 6){
            value = value.substring(0, len-6)+','+value.substring(len-6, len-3)+','+ value.substring(len-3);
        }
        else if(len > 3){
            value = value.substring(0, len-3)+','+ value.substring(len-3);
        }
        return value;
    },

    parseNumber(value){
        value = value+"";
        if(value == null) return null;
        var len = value.length;
        //if(len > 9){
        //    value = value.substring(0, len-9)+','+ value.substring(len-9, len-6)+','
        //        +value.substring(len-6, len-3)+','+ value.substring(len-3)
        //}
        //else if(len > 6){
        //    value = value.substring(0, len-6)+','+value.substring(len-6, len-3)+','+ value.substring(len-3);
        //}
        //else if(len > 3){
        //    value = value.substring(0, len-3)+','+ value.substring(len-3);
        //}
        if(len > 4)
            value = value/10000 + '万';
        else
            value = '';

        return value;
    },


    updateTitle(router, value){
        var name;
        switch (router) {
            case 'home':
                name = '首页'; break;
            case 'latest':
                name = '最新收录'; break;
            case 'recommend':
                name = '推荐'; break;
            case 'demoDay':
                name = 'Demo Day'; break;
            case 'search':
                name = '搜索';
                if(value != null){
                    name += ' - '+value;
                }
                break;
            case 'coldcall':
                name ='Cold Call';
                if(value != null){
                    name += ' - '+value;
                }
                break;
            case 'title':
                name = value;
                break;

            case 'createCompany':
                name = '新建公司';
                break;

            case 'org':
                name='机构';
                break;

            case 'setting':
                name = '设置';
                break;

            case 'collection':
                name = '发现'; break;

            case 'newCollection':
                name = '自定义集合'; break;

            default :
                break;
        }

        if(this.isNull(name))
            document.title = '无标题';
        else
            document.title = name + ' - ' + '烯牛数据';
    },


    getRoundName(round){
        var roundName;
        switch (Number(round)) {
            case 0:
                roundName = 'N/A';
                break;
            case 1000:
                roundName = '未融资';
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
    getArtifactTypeName(type){
        var typeName;
        switch (Number(type)) {
            case 4000:
                typeName = '全部';
                break;
            case 4010:
                typeName = '网站';
                break;
            case 4020:
                typeName = '微信';
                break;
            case 4030:
                typeName = '微博';
                break;
            case 4040:
                typeName = 'iOS';
                break;
            case 4050:
                typeName = '安卓';
                break;
            case 4060:
                typeName = 'windows Phone';
                break;
            case 4070:
                typeName = 'PC';
                break;
            case 4080:
                typeName = 'Mac';
                break;
            case 4099:
                typeName = '其他';
                break;
        }
        return typeName;
    },

    getArtifactLogo(type){
        var className;
        switch (Number(type)) {
            case 4010:
                className = 'fa-link link-color';
                break;
            case 4020:
                className = 'fa-weixin weixin-color';
                break;
            case 4030:
                className = 'fa-weibo weibo-color';
                break;
            case 4040:
                className = 'fa-apple app-color';
                break;
            case 4050:
                className = 'fa-android android-color';
                break;
            case 4060:
                className = 'fa-mobile-phone phone-color';
                break;
            case 4070:
                className = 'fa-windows pc-color';
                break;
            case 4080:
                className = 'fa-apple app-color';
                break;
            default :
                className ='';
                break;
        }
        return className;
    },

    parseMarkContent(markContent){
        var score;
        switch (markContent){
            case '重点跟进':
                score= 4; break;
            case '太烂了':
                score= 2; break;
            case '随便聊聊':
                score= 3; break;
            case '不关心':
                score=1;break;
        }
        return score;
    },

    getCurrencyStyle(value){
        var className;
        switch (Number(value)) {
            case 3010:
                className = 'fa-usd';
                break;
            case 3020:
                className = 'fa-cny';
                break;
            case 3030:
                className = 'fa-usd';
                break;
            default :
                className ='';
                break;
        }
      return className;
    },

    getJobFieldName(value){
        var name;
        switch (value){
            case 15010:
                name= '技术'; break;
            case 15020:
                name= '产品'; break;
            case 15030:
                name= '设计'; break;
            case 15040:
                name= '行政'; break;
            case 15050:
                name= '市场'; break;
            case 15060:
                name= '职能'; break;
            case 15070:
                name= '金融'; break;
            default:
                name= '未知'; break;
        }
        return name;
    },

    getEducationName(value){
        var name;
        switch (value){
            case 6010:
                name= '高中'; break;
            case 6020:
                name= '高职'; break;
            case 6030:
                name= '本科'; break;
            case 6040:
                name= '硕士'; break;
            case 6050:
                name= '博士'; break;
            default:
                name= '未知'; break;
        }
        return name;
    },



    /****************** select *******************/

    searchTypeSelect(){
        return [{value:1, name:'公司名称'},
                {value:2, name:'标签'}]
    },

    roundSelect(){
        return [
            {value: 1000, name: '未融资'},
            {value: 1010, name: '天使轮'},
            {value: 1020, name: 'Pre-A轮'},
            {value: 1030, name: 'A轮'},
            //{value: 1031, name: 'A+轮'},
            {value: 1040, name: 'B轮'},
            {value: 1050, name: 'C轮'},
            {value: 1060, name: 'D轮以上'},
            //{value: 1070, name: 'E轮'},
            //{value: 1080, name: 'F轮'},
            //{value: 1090, name: '后期阶段'},
            {value: 1100, name: 'Pre-IPO'},
            {value: 1110, name: 'IPO'},
            {value: 1120, name: '被收购'}
        ];

    },

    updateRoundSelect(){
        return [
                {value: 0, name: '请选择'},
                {value: 1000, name: '未融资'},
                {value: 1010, name: '天使轮'},
                {value: 1020, name: 'Pre-A轮'},
                {value: 1030, name: 'A轮'},
                //{value: 1031, name: 'A+轮'},
                {value: 1040, name: 'B轮'},
                {value: 1050, name: 'C轮'},
                {value: 1060, name: 'D轮以上'},
                //{value: 1070, name: 'E轮'},
                //{value: 1080, name: 'F轮'},
                //{value: 1090, name: '后期阶段'},
                //{value: 1100, name: 'Pre-IPO'},
                {value: 1110, name: 'IPO'},
                {value: 1120, name: '被收购'}
            ];

    },

    productSelect(){
        return [
            {value: 4010, name: '网站'},
            {value: 4020, name: '微信'},
            {value: 4030, name: '微博'},
            {value: 4040, name: 'iOS'},
            {value: 4050, name: 'android'},
            //{value: 4060, name: ''},
            //{value: 4070, name: ''},
            //{value: 4080, name: '未融资'},
            {value: 4099, name: '其他'}
        ]
    },


    currencySelect(){
        var currencySelect = [
            {value: 0, name: '请选择货币'},
            {value: 3020, name: '人民币'},
            {value: 3010, name: '美元'}

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
            //{value: 4, name:'地点'},
            //{value: 5, name:'投资方'},
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

    dateSelect(){
        var date = new Date().getFullYear();
        var dateSelect= [];
        for(var i=0; i<5; i++){
            dateSelect.push(date--);
        }
        return dateSelect;
    },


    /**************  useful list ************/
    locationUseful(){
        var data = [
            {name: '北京', value: 1},
            {name: '上海', value: 2},
            {name: '深圳', value: 63},
            {name: '杭州', value: 360},
            {name: '广州', value: 52},
            {name: '成都', value: 296},
            {name: '南京', value: 185},
            {name: '武汉', value: 146}
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
    },

    dateFormat1(dateLong){
        return new Date(dateLong).format("yyyy-MM-dd hh:mm:ss");
    },

    dateFormat2(dateLong){
        return new Date(dateLong).format("yyyy-MM-dd hh:mm");
    },

    dateFormat3(dateLong){
        return new Date(dateLong).format("yyyy-MM-dd");
    },

    dateFormat5(dateLong){
        return new Date(dateLong).format("MM-dd hh:mm");
    },

    getWeekday(date){
        var days = ['周日','周一','周二','周三','周四','周五','周六'];
        return days[new Date(date).getDay()];
    },

    changeTwoDecimal(x){
        var f_x = parseFloat(x);
        if (isNaN(f_x))
        {
            return '';
        }
        f_x = Math.round(f_x *100)/100;

        return f_x;
    },

    browserVersion(){
        if(/AppleWebKit.*Mobile/i.test(navigator.userAgent) || (/MIDP|SymbianOS|NOKIA|SAMSUNG|LG|NEC|TCL|Alcatel|BIRD|DBTEL|Dopod|PHILIPS|HAIER|LENOVO|MOT-|Nokia|SonyEricsson|SIE-|Amoi|ZTE/.test(navigator.userAgent))){
            //if(window.location.href.indexOf("?mobile")<0){
                //try{
                //    if(/Android|webOS|iPhone|iPod|BlackBerry/i.test(navigator.userAgent)){
                //       return 'mobile'
                //    }else if(/iPad/i.test(navigator.userAgent)){
                //    }else{
                //
                //    }
                //}catch(e){}
                return 'mobile';
            //}
        }
        return 'pc';
    }


};









module.exports = Functions;




