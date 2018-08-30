var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');
var Functions = require('../../../../../../react-kit/util/Functions');
var DemoDayActions = require('../../../../action/DemoDayActions');
var DemodayStore = require('../../../../store/DemoDayStore');

var DemodayUtil = require('../../../../util/DemodayUtil');

const RejectOrgList = React.createClass({
    mixins: [Reflux.connect(DemodayStore, 'data')],

    render(){
        var state = this.state;
        if (Functions.isEmptyObject(state))
            return null;
        var userScores = this.state.data.userScores;
        if (Functions.isEmptyObject(userScores)) return null;

        return (
            <div className="dd-score-list">
                <div className="preScore-item  dd-list-head">
                    <div className="preScore-item-rank ">序号</div>
                    <div ><i className="fa fa-user" /></div>
                    <div>分数</div>
                    <div>分数</div>
                </div>
                {userScores.map(function (result, index) {
                    return <UserPreScoreItem key={index} data={result}
                                        index={index}
                                         />
                })

                }
            </div>
        )

    }

});
const UserPreScoreItem =React.createClass({
    render(){
        var index = this.props.index + 1;
        var userScore =this.props.data;

        return (
            <div className="preScore-item  ">
                <div className="preScore-item-rank">{index}</div>
                <div>{userScore.userName}</div>
                <div>{userScore.score}</div>
            </div>
        )
    }
});
module.exports = RejectOrgList;


