var React = require('react');
var Reflux = require('reflux');

var Functions = require('../../../../../../react-kit/util/Functions');
var DemoDayActions = require('../../../../action/DemoDayActions');
var DemodayUtil = require('../../../../util/DemodayUtil');


const DemoDayPreScoreDone = React.createClass({

    render(){
        var demodayCompanies = this.props.demodayCompanies;
        if (!demodayCompanies) return null;
        var demodayStatus =this.props.demodayStatus;
        var update;
        var demodayId=this.props.demodayId;
        if(demodayStatus==26020){
           var href= "/admin/#/demoday/" + demodayId+"/preScores";
            update=  <span>
                 <a className="text-blue"  href={href}>
                     <i className="fa fa-pencil-square-o">更改初筛状态</i>
                 </a>
                </span>
        }
        return (
            <div className="m-t-15">
                <span className="admin-head">
                  <h3> 备选公司</h3>
                 </span>
                 {update}
                <div className="dd-score-list">
                    <div className="preScore-item  dd-list-head">
                        <div className="admin-demoday-org-rank">序号</div>
                        <div>项目名</div>
                        <div>推荐机构</div>
                        <div>初筛状态</div>
                    </div>
                    {
                        demodayCompanies.map(function (result, index) {
                            return <CompanyItem key={index}
                                                index={index}
                                                data={result}
                                                demodayId={demodayId}
                                />
                        })}
                </div>
            </div>
        )
    }
});


const CompanyItem = React.createClass({


    render(){
        var index = this.props.index + 1;
        var data = this.props.data;
        var href = "/#/demoday/"+this.props.demodayId+"/company/"+data.code+"/preScore";
       var  scoringStatus ;
        if ( data.scoringStatus == 27020) {
            scoringStatus =
                <li className="fa fa-check cc-text-green">pass</li>;

        }
        else if ( data.scoringStatus == 27030) {
            scoringStatus = <li className="fa fa-times text-red">
                reject
            </li>;
        }
        else scoringStatus="初筛选中";


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
            </div>
        )
    }


});



module.exports = DemoDayPreScoreDone;

