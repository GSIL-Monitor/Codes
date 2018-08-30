var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ReactHighcharts = require('react-highcharts');
var ProductUtil = require('../../../../../util/ProductUtil');
var TrendsCharts = require('../TrendsCharts.react');
var DivFindNone = require('../../../../../../../react-kit/basic/DivFindNone.react');

const WebSiteTrends = React.createClass({

    render(){
        var artifact = this.props.artifact;
        var trends = this.props.trends;
        var dateList = this.props.dateList;
        var alexaData = ProductUtil.getAlexa(trends.alexaList, dateList);
        var rankCNList = alexaData.rankCNList;
        var rankGlobalList = alexaData.rankGlobalList;
        var dayList = this.props.dayList;
        var trendsChart;
        //无数据
        if (ProductUtil.checkListEmpty(rankCNList) && ProductUtil.checkListEmpty(rankGlobalList)) {
            trendsChart = <DivFindNone />
        }
        else {
            var trendName = '排名';
            var text = '名次';
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
                    plotLines: [{value: 0, width: 1, color: '#808080'}],
                    reversed: true
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
                    {name: '中国', data: rankCNList,lineWidth:1},
                    {name: '全球', data: rankGlobalList,lineWidth:1}
                    //{name:'dailyIP', data: alexaData.dailyIPList},
                    //{name:'dailyPV', data: alexaData.dailyPVList}
                ]
            };
            trendsChart = <ReactHighcharts config={config}/>
        }

        return <TrendsCharts trendsChart={trendsChart} onClick={this.props.onClick}
                           selected = {this.props.selected}
            />
    }
});
module.exports = WebSiteTrends;