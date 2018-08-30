var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ReactHighcharts = require('react-highcharts');
var ProductUtil = require('../../../../../util/ProductUtil');
var TrendsCharts = require('../TrendsCharts.react');
var DivFindNone = require('../../../../../../../react-kit/basic/DivFindNone.react');

const IosTrends = React.createClass({
    render(){
        var artifact = this.props.artifact;
        var trends = this.props.trends;
        var dateList = this.props.dateList;
        var dayList = this.props.dayList;
        var scoreList = ProductUtil.getIos(trends.iosList, dateList);

        var trendsChart;
        if (ProductUtil.checkListEmpty(scoreList)) {
            trendsChart = <DivFindNone />;
        }
        else {
            var trendName = '评分';
            var text = '分数';
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
                    plotLines: [{
                        value: 0,
                        width: 1,
                        color: '#808080'
                    }]
                },
                legend: {
                    layout: 'vertical', align: 'right', verticalAlign: 'middle', borderWidth: 0
                },
                plotOptions: {
                    series: {
                        marker: {
                            radius: 2
                        }
                    }
                },
                series: [
                    {name: 'IOS', data: scoreList,lineWidth:1}
                ]
            };
            trendsChart = <ReactHighcharts config={config}/>
        }
        return <TrendsCharts trendsChart={trendsChart} onClick={this.props.onClick}  selected = {this.props.selected} />

    }
});

module.exports = IosTrends;