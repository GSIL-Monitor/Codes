var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var DemoDayActions = require('../../../../../webapp-site/js/action/demoday/DemoDayActions');
var Functions = require('../../../../../react-kit/util/Functions');
var StarRating = require('./StarRating.react');

const Score = React.createClass({

    render(){
        var data = this.props.data;
        var submit;

        if(data.submitScore)
            submit = <button className="btn btn-navy score-submit" onClick={this.submitScore}>提交</button> ;


        var disable = true;
        if(data.scoringStatus == 27040){
            disable = false;
        }

        var preScore = data.preScore;
        if(preScore == null)
            preScore = 'N/A';

        return(
            <div className='m-t--20'>
                <div className="m-b-10 ft-14">你的初筛分数：{preScore}</div>

                <StarRating name="行业" type="industry" disable={disable} rated={data.score[0]}  rating={data.ratingIndustry}/>
                <StarRating name="团队" type="team" disable={disable} rated={data.score[1]}  rating={data.ratingTeam}/>
                <StarRating name="产品" type="product" disable={disable} rated={data.score[2]}  rating={data.ratingProduct}/>
                <StarRating name="盈利" type="gain" disable={disable} rated={data.score[3]}  rating={data.ratingGain}/>
                <StarRating name="估值" type="preMoney" disable={disable} rated={data.score[4]}  rating={data.ratingPreMoney}/>

                {submit}

                <div className="score-decide">
                    <button className="btn btn-red score-submit" onClick={this.decide}>投资决策</button>
                </div>

            </div>
        )
    },

    submitScore(){
        DemoDayActions.submitScore();
    },

    decide(){
        $('#decision-modal').show();
    }

});



module.exports = Score;

