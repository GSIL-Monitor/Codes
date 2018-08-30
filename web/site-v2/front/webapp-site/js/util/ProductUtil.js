var Functions = require('../../../react-kit/util/Functions');
const ProductUtil = {

    getDatesets(data){
        var datasets = [];
        var labels = [];
        for (var i in data) {
            if (i < 7) {
                datasets.push(data[i].download);
                labels.push(data[i].date);
            }
        }

        return {labels: labels, datasets: datasets};
    },


    chartOptions: {

        ///Boolean - Whether grid lines are shown across the chart
        scaleShowGridLines: true,

        //String - Colour of the grid lines
        scaleGridLineColor: "rgba(0,0,0,.05)",

        //Number - Width of the grid lines
        scaleGridLineWidth: 1,

        //Boolean - Whether to show horizontal lines (except X axis)
        scaleShowHorizontalLines: true,

        //Boolean - Whether to show vertical lines (except Y axis)
        scaleShowVerticalLines: true,

        //Boolean - Whether the line is curved between points
        bezierCurve: true,

        //Number - Tension of the bezier curve between points
        bezierCurveTension: 0.4,

        //Boolean - Whether to show a dot for each point
        pointDot: true,

        //Number - Radius of each point dot in pixels
        pointDotRadius: 4,

        //Number - Pixel width of point dot stroke
        pointDotStrokeWidth: 1,

        //Number - amount extra to add to the radius to cater for hit detection outside the drawn point
        pointHitDetectionRadius: 20,

        //Boolean - Whether to show a stroke for datasets
        datasetStroke: true,

        //Number - Pixel width of dataset stroke
        datasetStrokeWidth: 2,

        //Boolean - Whether to fill the dataset with a colour
        datasetFill: true

    },

    getAlexa(list, dateList){
        var rankCNList = [];
        var rankGlobalList = [];
        var dailyIPList = [];
        var dailyPVList = [];
        var flag;
        //补全list，没有的则用null代替,将数据和x轴一一对应
        for (var i  in dateList) {
            flag = false;
            var date = dateList[i];
            for (var j in list) {
                if (date == Functions.dateFormat3(list[j].date)) {
                    rankCNList.push(list[j].rankCN);
                    rankGlobalList.push(list[j].rankGlobal);
                    dailyIPList.push(list[j].dailyIP);
                    dailyPVList.push(list[j].dailyPV);
                    flag = true;
                    break;
                }
                else {
                    flag = false;
                }
            }
            if (!flag) {
                rankCNList.push(null);
                rankGlobalList.push(null);
            }
        }
        return {
            rankCNList: rankCNList,
            rankGlobalList: rankGlobalList,
            dailyIPList: dailyIPList,
            dailyPVList: dailyPVList
        };
    },

    getAndroid(list, dateList){
        var downloadList = [];
        var scoreList = [];
        var flag;
        //补全list，没有的则用null代替,将数据和x轴一一对应
        for (var i  in dateList) {
            flag = false;
            var date = dateList[i];
            for (var j in list) {
                if (date == Functions.dateFormat3(list[j].date)) {
                    downloadList.push(list[j].download);
                    scoreList.push(list[j].score);
                    flag = true;
                    break;
                }
                else {
                    flag = false;
                }
            }
            if (!flag) {
                downloadList.push(null);
                scoreList.push(null);
            }
        }

        return {
            downloadList: downloadList,
            scoreList: scoreList
        };
    },

    getCategories(expand){
        var now = new Date();
        var dateList = [];
        for (var i = expand; i > 0; i--) {
            var date = new Date();
            date.setDate(now.getDate() - i);
            dateList.push(Functions.dateFormat3(date));
        }
        return dateList;
    },

    getIos(list, dateList){
        var scoreList = [];
        var flag;
        //补全list，没有的则用null代替,将数据和x轴一一对应
        for (var i in dateList) {
            flag = false;
            var date = dateList[i];
            for (var j in list) {
                if (date == Functions.dateFormat3(list[j].date)) {
                    scoreList.push(list[j].score);
                    flag = true;
                    break;
                }
                else {
                    flag = false;
                }
            }
            if (!flag) {
                scoreList.push(null);
            }
        }
        return scoreList;
    },

    getDayList(list){
        var dayList = [];
        for (var i in list) {
            dayList.push(list[i].substring(5, 10));
        }
        return dayList;
    },

    checkListEmpty(list){
        var empty = true;
        for (var i in list) {
            if (list[i] != null) {
                empty = false;
                break;
            }
        }
        return empty;
    },

    // 如果不用重新发送请求，那么data中有各个type对应的list
    checkedData(data){
        if (data.trendsDay == null || data.trendsMonth == null)return true;
    },

    trendsType(){
        return {
            //记录操作类型
            dataType: null
        }
    },

    setResult(id, type, store){

        var list = store.list;
        //var trendsDay = this.trendsType();
        var trendsMonth = this.trendsType();
        //var dayLength = 10;
        switch (type) {
            case 4010:
                trendsMonth.alexaList = store.alexaList;
                //trendsDay.alexaList = this.subList(store.alexaList, dayLength);
            case 4050:
                trendsMonth.sanliulingList = store.sanliulingList;
                trendsMonth.baiduList = store.baiduList;
                trendsMonth.wandoujiaList = store.wandoujiaList;
                trendsMonth.myappList = store.myappList;
                trendsMonth.dataType = 'download';
                //trendsDay.sanliulingList = this.subList(store.sanliulingList, dayLength);
                //trendsDay.baiduList = this.subList(store.baiduList, dayLength);
                //trendsDay.wandoujiaList = this.subList(store.wandoujiaList, dayLength);
                //trendsDay.myappList = this.subList(store.myappList, dayLength);
                //trendsDay.dataType = 'download';

            case 4040:
                trendsMonth.iosList = store.iosList;
                //trendsDay.iosList = this.subList(store.iosList, dayLength);
        }
        for (var i in list) {
            if (list[i].artifact.id == id) {
                //list[i].trendsDay = trendsDay;
                list[i].trendsMonth = trendsMonth;
                //默认是显示一个月数据
                list[i].selected = 'month';
            }
        }
    },

    //subList(list, length){
    //    if (list.length <= length) {
    //        return list;
    //    }
    //    else {
    //        var result = [];
    //        for (var i = 0; i < length; i++) {
    //            result.push(list[i]);
    //        }
    //        return result;
    //    }
    //
    //},

    getImages(list){
        var images = [];
        //images.push('/file/'+'566fe1a0e4861d3fe7faf5a2');
        //images.push('/file/'+'566fe1b1e4861d3fe7faf5a4');
        //images.push('/file/'+'566fe1b8e4861d3fe7faf5a6');
        for (var i in list) {
            images.push('/file/' + list[i].link);
        }
        return images;
    },

    needUpdate(nextProps, props){
        var nextImages = nextProps.images;
        var images = props.images;
        if (nextImages.length != images.length) {
            return true
        } else {
            var isSame;
            var cached = [];
            //判断长度相同的props中images是否相同
            for (var i in nextImages) {
                isSame = false;
                var image = nextImages[i];
                for (var k in  images) {
                    if (image == images[k]) {
                        isSame = true;
                        break;
                    }
                }
                if (isSame) {
                    cached.push(image);
                }

            }
            if (cached.length == nextImages.length) return false;
            else return true;

        }
    },

    getTotal(store){
        var count = store.website.count +
            store.weibo.count +
            store.wechat.count +
            store.ios.count +
            store.android.count +
            store.windowsPhone.count +
            store.pc.count +
            store.mac.count +
            store.other.count;

        var list = [];
        list = list.concat(store.website.list.reverse())
                    .concat(store.ios.list)
                    .concat(store.weibo.list)
                    .concat(store.wechat.list)
                    .concat(store.android.list)
                    .concat(store.windowsPhone.list)
                    .concat(store.pc.list)
                    .concat(store.mac.list)
                    .concat(store.other.list);


        list = list.slice(0, 20)
        return {list: list, count: count};
    },

    changeType(store){
        var selectedType = store.selectedType;
        var list = [];
        var count = 0;
        switch (Number(selectedType)) {
            case 4000:
                list = store.total.list;
                count = store.total.count;
                break;
            case 4010:
                list = store.website.list.reverse();
                count = store.website.count;
                break;
            case 4020:
                list = store.wechat.list;
                count = store.wechat.count;
                break;
            case 4030:
                list = store.weibo.list;
                count = store.weibo.count;
                break;
            case 4040:
                list = store.ios.list;
                count = store.ios.count;
                break;
            case 4050:
                list = store.android.list;
                count = store.android.count;
                break;
            case 4060:
                list = store.windowsPhone.list;
                count = store.windowsPhone.count;
                break;
            case 4070:
                list = store.pc.list;
                count = store.pc.count;
                break;
            case 4080:
                list = store.mac.list;
                count = store.mac.count;
                break;
            default:
                list = store.other.list;
                count = store.other.count;
                break;
        }
        return {list: list, count: count};
    }

};

module.exports = ProductUtil;