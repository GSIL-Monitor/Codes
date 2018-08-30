var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');
var ReactHighcharts = require('react-highcharts');

var Functions = require('../../../../../../react-kit/util/Functions');
var ProductActions = require('../../../../action/company/ProductActions');
var ProductUtil = require('../../../../util/ProductUtil');
var DivFindNone = require('../../../../../../react-kit/basic/DivFindNone.react');
var Loading = require('../../../../../../react-kit/basic/Loading.react');
/**** component ***/
var WebSiteTrends =require('./type/WebsiteTrends.react');
var AndroidTrends = require('./type/AndroidTrends.react');
var IosTrends = require('./type/IosTrends.react');


const BasicTrends = React.createClass({

    render(){

        var data = this.props.data;
        if(!data.selected) return <Loading />;
        var selected = data.selected;
        var trends;
        var expand;
        var tickInterval;
        var artifact = data.artifact;
        var artifactType = artifact.type;

        //if (selected == 'day') {
        //    trends = data.trendsDay;
        //    expand = 10;
        //    tickInterval = 1;
        //}else
        if (selected == 'month') {
            trends = data.trendsMonth;
            expand=30;
            tickInterval = 2;
        }

        var dateList = ProductUtil.getCategories(expand);
        var dayList = ProductUtil.getDayList(dateList);

        //alexa
        if (artifactType == 4010) {
            return <WebSiteTrends  artifact={artifact} trends={trends} dateList={dateList} onClick={this.click}
                           tickInterval={tickInterval} dayList={dayList} selected={selected}
                />
        }
        // android
        else if (artifactType == 4050) {
            return <AndroidTrends  artifact={artifact} trends={trends} dateList={dateList} onClick={this.click}
                             tickInterval={tickInterval} dayList={dayList} selected={selected}
                />
        }
        //ios
        else if (artifactType == 4040) {
            return <IosTrends   artifact={artifact} trends={trends} dateList={dateList} onClick={this.click}
                          tickInterval={tickInterval} dayList={dayList} selected={selected}
                />
        }
        else {
            return null;
        }
    }

    //click(expand){
    //    var data = this.props.data;
    //    if(data.selected==expand) return;
    //    var artifact = data.artifact;
    //    if(expand=='month'){
    //        ProductActions.changeExpand(artifact.id,expand);
    //    }
    //    else if(expand=='day'){
    //        ProductActions.changeExpand(artifact.id,expand);
    //    }
    //}
});
module.exports = BasicTrends;