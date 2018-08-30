var React = require('react');
var Reflux = require('reflux');

var DemoDayActions = require('../../../../../webapp-site/js/action/demoday/DemoDayActions');
var DemoDayUtil = require('../../../../../webapp-site/js/util/DemoDayUtil');
var CompanyUtil = require('../../../../../webapp-site/js/util/CompanyUtil');
var StarRating = require('../score/StarRating.react');

var Functions = require('../../../../../react-kit/util/Functions');

const Scores = React.createClass({

    render(){
        var list = this.props.list;
        if(list == null) return null;
        if(list.length ==0) return null;
        list = DemoDayUtil.sortScores(list);
        var id = this.props.id;
        return(
                <div className="dd-score-list">
                    <div className="score-item dd-list-head m-score-item">
                        <div className="m-score-name">项目名</div>
                        <div className="m-score-org">推荐机构</div>
                        <div className="m-score-funding">融资</div>
                        <div className="m-score-detail">(初筛) 项目打分</div>
                    </div>

                    {list.map(function(result, index){
                        return <ScoreItem key={index}
                                          index={index}
                                          data={result}
                                          id={id}/>
                    })}
                </div>

        )
    }

});

const ScoreItem = React.createClass({
    render(){

        var index = this.props.index + 1;
        var data = this.props.data;
        var id = this.props.id;


        var fundingInfo;
        var investment = data.investment;
        if(investment == null)
            fundingInfo= '未知';
        else
            fundingInfo= CompanyUtil.parseFunding(data);

        var className= 'score-item m-score-item ';
        if(data.scoringStatus == 27030 || data.joinStatus == 28020){
            className += 'item-unSelect ';
        }

        var preScore = data.preScore;
        if(preScore == null)
            preScore = '';
        else
            preScore = '('+preScore+')';


        return(
            <div className={className}>
                <div className="m-score-name"><a onClick={this.click}> {data.name} </a></div>
                <div className="m-score-org">{data.orgName}</div>
                <div className="m-score-funding">{fundingInfo}</div>
                <div className="m-score-detail">
                    <ul className="bread-scrum">
                        <span className="m-r-5">{preScore}</span>
                        <li>{data.industry} </li>
                        <li>{data.team} </li>
                        <li>{data.product} </li>
                        <li>{data.gain} </li>
                        <li>{data.preMoney} </li>
                    </ul>
                </div>
            </div>
        )
    },

    click(){
        var data = this.props.data;
        var id = this.props.id;
        DemoDayActions.initScore(id, data.code, 'score');
        window.location.href =  "./#/demoday/"+id+"/company/"+data.code+"/score";
    }
});

module.exports = Scores;
