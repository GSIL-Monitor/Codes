var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var DemoDayActions= require('../../../../../webapp-site/js/action/demoday/DemoDayActions');
var DemoDayStore = require('../../../../../webapp-site/js/store/demoday/DemoDayStore');
var Functions = require('../../../../../react-kit/util/Functions');

const Decision = React.createClass({

    mixins: [Reflux.connect(DemoDayStore, 'data')],

    componentWillMount() {
        DemoDayActions.initScore(this.props.id, this.props.code, this.props.type);
    },

    componentWillReceiveProps(nextProps) {
        DemoDayActions.initScore(nextProps.id, nextProps.code, nextProps.type);
    },


    render(){
        var state = this.state;
        if(Functions.isEmptyObject(state))
            return null;

        var data = state.data;
        return(
            <div className="dd-decision">
                <DecisionList data={data}/>

                <h3>打分参考</h3>
                <Scores data={data}/>
            </div>
        )
    }
});


const DecisionList = React.createClass({
    render(){
        var decision = this.props.data.decision;
        if(decision == null)
            return null;
        var results = decision.orgResults;

        var yeses= [];
        var noes = [];
        var others = [];

        if(results.length > 0){
            for(var i in results){
                if(results[i] == null){
                    others.push(results[i])
                }else if(results[i].result == 29020){
                    yeses.push(results[i])
                }else if(results[i].result == 29030){
                    noes.push(results[i])
                }
            }
        }

        var otherList, yesList, noList;
        if(yeses.length > 0){
            yesList= yeses.map(function(result, index){
                return <DecisionItem data={result} key={index} />
            })
        }

        if(noes.length > 0){
            noList= noes.map(function(result, index){
                return <DecisionItem data={result} key={index} />
            })
        }

        var partner = this.props.data.partner;
        var yesButton;
        var noButton;
        if(partner){
            yesButton = <button className="btn btn-red" onClick={this.yes}>发TS</button>;
            noButton = <button className="btn btn-gray" onClick={this.no}>不发TS</button>;
        }else{
            yesButton = <button className="btn btn-red" disabled="disabled">发TS</button>;
            noButton = <button className="btn btn-gray" disabled="disabled">不发TS</button>;
        }

        return(
            <div className="decision-list">

                <div className="vote-list">
                    {yesButton}
                    {yesList}
                </div>

                <div className="vote-list">
                    {noButton}
                    {noList}
                </div>

                <div className="">
                </div>

            </div>
        )
    },

    yes(){
        DemoDayActions.decide(29020);
    },

    no(){
        DemoDayActions.decide(29030);
    }
});


const DecisionItem = React.createClass({
    render(){
        return(
            <div className="decision-item">{this.props.data.orgName}</div>
        )
    }
});


const Scores = React.createClass({
    render(){
        var decision = this.props.data.decision;
        if(decision == null)
            return null;
        var scores = decision.scoreList;

        var scoreList =  <div className="text-center m-t-10 m-b-10"><h3>暂无数据</h3></div>;
        var average = null;
        var len = scores.length;
        if(len > 0){
            scoreList = scores.map(function(result, index){
                return <ScoreItem data={result} key={index}/>
            });

            var industryAverage = 0;
            var teamAverage = 0;
            var productAverage = 0;
            var gainAverage = 0;
            var preMoneyAverage = 0;
            for(var i in scores){
                industryAverage += scores[i].industry;
                teamAverage += scores[i].team;
                productAverage += scores[i].product;
                gainAverage += scores[i].gain;
                preMoneyAverage += scores[i].preMoney;
            }

            var scoreAverage = {};
            scoreAverage.userName = '平均';
            scoreAverage.industry = Functions.changeTwoDecimal(industryAverage/len);
            scoreAverage.team = Functions.changeTwoDecimal(teamAverage/len);
            scoreAverage.product = Functions.changeTwoDecimal(productAverage/len);
            scoreAverage.gain = Functions.changeTwoDecimal(gainAverage/len);
            scoreAverage.preMoney = Functions.changeTwoDecimal(preMoneyAverage/len);

            average = <ScoreItem data={scoreAverage}/>
        }

        return(
            <div className="dd-company-score-list">
                <div className="dd-company-score-item">
                    <div><i className="fa fa-user fa-lg"></i></div>
                    <div>行业</div>
                    <div>团队</div>
                    <div>产品</div>
                    <div>盈利</div>
                    <div>估值</div>
                </div>

                {scoreList}
                {average}
            </div>
        )

    }
});

const ScoreItem = React.createClass({
    render(){
        var data = this.props.data;
        return(
            <div className="dd-company-score-item">
                <div>
                    {data.userName}
                </div>
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

module.exports = Decision;

