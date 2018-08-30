var React = require('react');
var Reflux = require('reflux');

var DemoDayUtil = require('../../../util/DemoDayUtil');
var CompanyUtil = require('../../../util/CompanyUtil');
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
                    <div className="score-item dd-list-head">
                        <div className="score-item-rank">序号</div>
                        <div>项目名</div>
                        <div>推荐机构</div>
                        <div>公司地址</div>
                        <div>融资金额</div>
                        <div>初筛分数</div>
                        <div>行业打分</div>
                        <div>团队打分</div>
                        <div>产品打分</div>
                        <div>盈利打分</div>
                        <div>估值打分</div>
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
        var link = "/#/demoday/"+id+"/company/"+data.code+"/score";

        var fundingInfo;
        var investment = data.investment;
        if(investment == null)
            fundingInfo= '未知';
        else
            fundingInfo= CompanyUtil.parseFunding(data);

        var className= 'score-item ';
        if(data.scoringStatus == 27030 || data.joinStatus == 28020){
            className += 'item-unSelect ';
        }

        var preScore = data.preScore;
        if(preScore == null)
            preScore = 'N/A';


        return(
            <div className={className}>
                <div className="score-item-rank">{index}</div>
                <div className="dd-item-name">
                    <a href={link}> {data.name} </a>
                </div>
                <div>{data.orgName}</div>
                <div>{data.location}</div>
                <div>{fundingInfo}</div>
                <div>{preScore}</div>
                <div>
                    {data.industry}
                </div>
                <div>
                    {data.team}
                </div>
                <div>
                    {data.product}
                </div>
                <div>
                    {data.gain}
                </div>
                <div>
                    {data.preMoney}
                </div>
            </div>
        )
    }
});

module.exports = Scores;
