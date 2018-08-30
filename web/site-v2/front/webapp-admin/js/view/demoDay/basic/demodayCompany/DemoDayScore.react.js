var React = require('react');
var Reflux = require('reflux');

var Functions = require('../../../../../../react-kit/util/Functions');
var DemoDayActions = require('../../../../action/DemoDayActions');
var DemodayUtil = require('../../../../util/DemodayUtil');

var SelectedList =require('../../form/FormSelectedList.react.js');

const DemoDayScore = React.createClass({

    render(){
        var demodayCompanies = this.props.demodayCompanies;
        if (!demodayCompanies) return null;
        return (
            <div className="m-t-15">
                <span className="admin-head">
                  <h3> 备选公司</h3>
                 </span>
                <div className="dd-score-list">
                    <div className="preScore-item  dd-list-head">
                        <div className="admin-demoday-org-rank">序号</div>
                        <div>项目名</div>
                        <div>推荐机构</div>
                        <div>当前状态</div>
                        <div>参加状态</div>
                    </div>
                    {
                        demodayCompanies.map(function (result, index) {
                            return <CompanyItem key={index}
                                                index={index}
                                                data={result}
                                />
                        })}
                </div>
            </div>
        )
    }
});


const CompanyItem = React.createClass({


    render(){
        var  index = this.props.index + 1;
        var data = this.props.data;
        var href = "/#/demoday/" + this.props.demodayId + "/company/" + data.code + "/score";
        var scoringStatus;
        var joinStatus = DemodayUtil.getJoinStatus(data.joinStatus);
        if (data.scoringStatus == 27020) {
            scoringStatus =
                <li className="fa fa-check cc-text-green">pass</li>;
        }
        else if (data.scoringStatus == 27030) {
            scoringStatus = <li className="fa fa-times text-red">
                reject
            </li>;
            joinStatus = '';
        }
        else scoringStatus = DemodayUtil.getScoreStatus(data.scoringStatus);


        return (
            <div className="preScore-item">
                <div className="admin-demoday-org-rank">{index}</div>
                <div>
                    <a href={href}>{data.name} </a>
                </div>
                <div> {data.orgName}</div>
                <div>
                    {scoringStatus}
                </div>
                <div>
                    {joinStatus}
                </div>
            </div>
        )
    }
});


module.exports = DemoDayScore;

