var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');


const TrendsHighCharts = React.createClass({
    render(){
        var selected = this.props.selected;
        var dayClassName;
        var monthClassName;
        //if(selected=='day'){
        //    dayClassName ='m-r-15 link-color';
        //    monthClassName='text-dark';
        //}
        //else if(selected=='month'){
        //    dayClassName = 'm-r-15 text-dark';
        //    monthClassName='link-color';
        //}
        monthClassName="m-r-15 text-dark";
        var download;
        var score;
        var dataType = this.props.dataType;
        var downloadClass;
        var scoreClass;
        if(dataType=='download'){
            downloadClass='link-color';
            scoreClass = 'text-dark m-l-15';
        }
        else if(dataType=='score'){
            downloadClass='text-dark';
            scoreClass='m-l-15 link-color';
        }
        if (this.props.download) {
            download = <div>
                <a className={downloadClass} onClick={this.download}>{this.props.download}</a>
            </div>
        }
        if (this.props.score) {
            score = <div>
                <a className={scoreClass} onClick={this.score}>{this.props.score}</a>
            </div>
        }
        //<a className={dayClassName} onClick={this.monthToDay}>最近十天</a>
        return (
            <div>
                <div className="trends-header m-l-20">
                    {download}
                    {score}
                    <div className='trend-lastRecords'>
                        <span className={monthClassName} onClick={this.dayToMonth}>最近一月</span>
                    </div>
                </div>
                {this.props.trendsChart}
            </div>
        )
    },

    download(e){
        this.props.changeView(true);
    },

    score(e){
        this.props.changeView(false);
    },

    monthToDay(){
        this.props.onClick('day');
    },

    dayToMonth(){
        this.props.onClick('month');
    }

});


module.exports = TrendsHighCharts;