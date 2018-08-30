var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var UserCompanyStore = require('../../../../../webapp-site/js/store/UserCompanyStore');
var UserCompanyActions = require('../../../../../webapp-site/js/action/UserCompanyActions');
var NoteUtil = require('../../../../../webapp-site/js/util/NoteUtil');
var Functions = require('../../../../../react-kit/util/Functions');

const UserScoreContent = React.createClass({
    render(){
        var data = this.props.data;
        var scores = data.scores;

        var leftClassName = '';
        if(scores.length > 0){
            leftClassName = 'user-mark-left';
            scores = <div className="user-mark-right">
                {scores.map(function (result, index) {
                    return <ScoreItem key={index} data={result}/>
                })}
            </div>;
        }

        return(
            <div className="m-mark-list">
                {scores}
                <div className={leftClassName}>
                    <ScoreContent className="mark-info mark-left"
                                  content="重点跟进"
                                  score="4"
                        />
                    <ScoreContent className="mark-info mark-top"
                                  content="随便聊聊"
                                  score="3"
                        />
                    <ScoreContent className="mark-info mark-right"
                                  content="太烂了"
                                  score="2"
                        />
                    <ScoreContent className="mark-info mark-bottom"
                                  content="不关心"
                                  score="1"
                        />
                </div>


            </div>
        )
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
        $('.modal').hide();
    }
});


const ScoreItem = React.createClass({
    render(){
        var data = this.props.data;
        var className =  'deal-score-item '+NoteUtil.parseScoreColor(data.score);
        return(
            <div className={className}>{data.userName}</div>
        )
    }

});


module.exports = UserScoreContent;

