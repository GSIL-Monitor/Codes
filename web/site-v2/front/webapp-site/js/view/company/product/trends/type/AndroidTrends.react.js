var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ProductActions = require('../../../../../action/company/ProductActions');
var ReactHighcharts = require('react-highcharts');
var ProductUtil = require('../../../../../util/ProductUtil');
var TrendsCharts = require('../TrendsCharts.react');
var DivFindNone = require('../../../../../../../react-kit/basic/DivFindNone.react');


const AndroidTrends = React.createClass({
    render(){
        var artifact = this.props.artifact;
        var trends = this.props.trends;
        var dateList = this.props.dateList;
        var dayList = this.props.dayList;

        var sanliulingData = ProductUtil.getAndroid(trends.sanliulingList, dateList);
        var baiduData = ProductUtil.getAndroid(trends.baiduList, dateList);
        var wandoujiaData = ProductUtil.getAndroid(trends.wandoujiaList, dateList);
        var myappData = ProductUtil.getAndroid(trends.myappList, dateList);

        var trendName;
        var text;
        var sanliuling;
        var baidu;
        var wandoujia;
        var myapp;
        var score = '查看评分';
        var download = '查看下载量';
        if (trends.dataType == 'download') {
            trendName = "累计下载量";
            text = '累计下载量';
            sanliuling = sanliulingData.downloadList;
            baidu = baiduData.downloadList;
            wandoujia = wandoujiaData.downloadList;
            myapp = myappData.downloadList;
        }
        else if (trends.dataType == 'score') {
            trendName = '评分';
            text = '分数';
            sanliuling = sanliulingData.scoreList;
            baidu = baiduData.scoreList;
            wandoujia = wandoujiaData.scoreList;
            myapp = myappData.scoreList;
        }

        var trendsChart;
        if (ProductUtil.checkListEmpty(sanliuling) && ProductUtil.checkListEmpty(baidu) &&
            ProductUtil.checkListEmpty(wandoujia) && ProductUtil.checkListEmpty(myapp)) {
            trendsChart = <DivFindNone />;
        }
        else {
            var title;
            if (null == artifact.name) {
                title = trendName;
            }
            else {
                title = artifact.name + '-' + trendName;
            }

            var config = {
                chart: {type: 'line', height: 300},
                title: {text: title},
                credits: {text: '绿洲合投', href: ''},
                xAxis: {categories: dayList, tickInterval: this.props.tickInterval},
                yAxis: {
                    title: {text: text},
                    plotLines: [{value: 0, width: 1, color: '#808080'}]
                },
                legend: {layout: 'vertical', align: 'right', verticalAlign: 'middle', borderWidth: 0},
                plotOptions: {
                    series: {
                        marker: {
                            radius: 2
                        }
                    }
                },
                series: [
                    {name: "360", data: sanliuling,lineWidth:1},
                    {name: "百度", data: baidu,lineWidth:1},
                    {name: "豌豆荚", data: wandoujia,lineWidth:1},
                    {name: "应用宝", data: myapp,lineWidth:1}
                ]
            };
            trendsChart = <ReactHighcharts config={config}/>;
        }

        return <TrendsCharts trendsChart={trendsChart} onClick={this.props.onClick}
                           download={download} score={score} changeView={this.changeView}
                           selected = {this.props.selected} dataType ={trends.dataType}


            />
    },

    changeView(operate){
        //true 是下载，false是评分
        if (operate) {
            ProductActions.changeView(this.props.artifact.id, 'download');
        } else {
            ProductActions.changeView(this.props.artifact.id, 'score');
        }
    }
});

module.exports = AndroidTrends;