var React = require('react');
var ReactDom = require('react-dom');
var Reflux = require('reflux');
var $ = require('jquery');

var UserCompanyStore = require('../../../store/UserCompanyStore');
var UserCompanyActions = require('../../../action/UserCompanyActions');
var Functions = require('../../../../../react-kit/util/Functions');
var NoteUtil = require('../../../util/NoteUtil');

const Score = React.createClass({
    render(){
        var markClass = "user-mark user-mark1";
        var dealUserScore = this.props.score;
        if (dealUserScore != null) {
            markClass += NoteUtil.parseScoreColor(dealUserScore);
        }
        var scores = this.props.scores;
        var scoreSum;
        if (scores.length > 0) {
            scores = <div className="others-mark">
                {scores.map(function (result, index) {
                    return <ScoreItem key={index} data={result}/>
                })}
            </div>;

            scoreSum = <span className="score-sum"></span>;
        }

        return (
            <div>
                <div className={markClass}
                     ref='markClassList'
                     onMouseEnter={this.markShow}>
                    <span>评分</span>
                    {scoreSum}

                </div>
                <div className="mark-list" onMouseLeave={this.markHide}>
                    <ScoreContent className="mark-info mark-left"
                                  content="重点跟进"
                                  score="4"
                        />
                    <ScoreContent className="mark-info mark-right"
                                  content="太烂了"
                                  score="2"
                        />
                    <ScoreContent className="mark-info mark-top"
                                  content="随便聊聊"
                                  score="3"
                        />
                    <ScoreContent className="mark-info mark-bottom"
                                  content="不关心"
                                  score="1"
                        />
                    {scores}
                </div>
            </div>
        )
    },

    markShow(e){
        $('.mark-list').show();
        $('.user-note, .user-coldcall').hide();
        e.stopPropagation();
    },

    markHide(e){
        $('.mark-list').hide();
        $('.user-mark, .user-score, .user-note, .user-coldcall').show();
        e.stopPropagation();
    }


});

const ScoreContent = React.createClass({
    render(){
        return (
            <div className={this.props.className} onClick={this.handleScore}>
                {this.props.content}
            </div>
        )
    },
    handleScore(){
        UserCompanyActions.score(Number(this.props.score));
    }
});

const ScoreItem = React.createClass({
    render(){
        var data = this.props.data;
        if (data.owner) return null;

        var className = 'deal-score-item ' + NoteUtil.parseScoreColor(data.score);
        return (
            <div className={className}>{data.userName}</div>
        )
    }

});


module.exports = Score;