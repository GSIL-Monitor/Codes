var React = require('react');
var ReactDom = require('react-dom');
var Reflux = require('reflux');
var $ = require('jquery');

var UserCompanyStore = require('../../../../../webapp-site/js/store/UserCompanyStore');
var UserCompanyActions = require('../../../../../webapp-site/js/action/UserCompanyActions');
var NoteUtil = require('../../../../../webapp-site/js/util/NoteUtil');
var Functions = require('../../../../../react-kit/util/Functions');

const UserCompany = React.createClass({

    mixins: [Reflux.connect(UserCompanyStore, 'data')],

    componentWillMount() {
        UserCompanyActions.getScore(this.props.code);
    },

    componentWillReceiveProps(nextProps) {
        if(this.props.code == nextProps.code) return;
        UserCompanyActions.getScore(nextProps.code);
    },

    render() {

        if (Functions.isEmptyObject(this.state))
            return null;

        var me = this;
        var markClass = "user-mark user-mark1";
        var dealUserScore = this.state.data.score;
        if (dealUserScore != null) {
            markClass += NoteUtil.parseScoreColor(dealUserScore);
        }

        var scores = this.state.data.scores;
        var scoreSum;
        if(scores.length > 0){
            scores = <div className="others-mark">
                        {scores.map(function (result, index) {
                            return <ScoreItem key={index} data={result}/>
                        })}
                    </div>;

            scoreSum = <span className="score-sum"></span>;
        }

        return (
            <div className="user-operate">
                <div className={markClass}
                     onClick = {this.click} >
                    <span>评分</span>
                    {scoreSum}
                </div>


            </div>
        )
    },

    click(){
        $('#user-score-modal').show();
    }

});


const ScoreItem = React.createClass({
    render(){
        var data = this.props.data;
        if(data.owner) return null;

        var className;
        return(
            <div className={className}>{data.userName}</div>
        )
    }

});

module.exports = UserCompany;

