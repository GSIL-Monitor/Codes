var React = require('react');
var Reflux = require('reflux');

var Functions = require('../../../../../../react-kit/util/Functions');
var DemoDayActions = require('../../../../action/DemoDayActions');
var DemodayUtil = require('../../../../util/DemodayUtil');

var SelectedList =require('../../form/FormSelectedList.react.js');

const DemoDayConnect = React.createClass({

    render(){
        var demodayCompanies = this.props.demodayCompanies;
        if (!demodayCompanies) return null;
        var demodayStatus = this.props.demodayStatus;
        var updateCompany = this.props.updateCompany;
        var me = this;
        var rank;
        var operate;
        if (demodayStatus == 26027) {
            if (updateCompany) {
                rank = "选中";
                operate = <span>
                        <a className="cc-text-green m-r-20" onClick={this.join}>参加</a>
                        <a className="text-red m-r-20" onClick={this.reject}>不参加</a>
                        <a className="text-blue" onClick={this.click}>取消</a>
                    </span>;
            }
            else {
                rank = "序号";
                operate = <span>
                 <a className="text-blue" onClick={this.click}>
                     <i className="fa fa-pencil-square-o">更改参加状态</i>
                 </a>
                </span>;
            }

        }
        else {
            rank = "序号";
        }

        return (
            <div className="m-t-15">
                <span className="admin-head">
                  <h3> 备选公司</h3>
                 </span>
                {operate}
                <div className="dd-score-list">
                    <div className="preScore-item  dd-list-head">
                        <div className="admin-demoday-org-rank">{rank}</div>
                        <div>项目名</div>
                        <div>推荐机构</div>
                        <div>初筛状态</div>
                        <div>参加状态</div>
                    </div>
                    {
                        demodayCompanies.map(function (result, index) {
                            return <CompanyItem key={index}
                                                index={index}
                                                data={result}
                                                updateCompany={updateCompany}
                                                selectedIds={me.props.selectedIds}
                                />
                        })}
                </div>
            </div>
        )
    },
    join(){
        DemoDayActions.batchJoinOrNot(28030);
    },
    reject(){
        DemoDayActions.batchJoinOrNot(28020);
    },
    click(){
        DemoDayActions.update("company");
    }
});


const CompanyItem = React.createClass({


    render(){
        var index = this.props.index + 1;
        var data = this.props.data;
        var href = "/#/demoday/" + this.props.demodayId + "/company/" + data.code + "/preScore";
        var scoringStatus;
        var joinStatus = DemodayUtil.getJoinStatus(data.joinStatus);
        var updateCompany = this.props.updateCompany;

        if (data.scoringStatus == 27020) {
            scoringStatus =
                <li className="fa fa-check cc-text-green">pass</li>;
            if (updateCompany) {
                index =<div className="m-l-20 ">
                    <SelectedList selectedIds={this.props.selectedIds} id={data.id} select={this.select}/>
                    </div>
            }
        }
        else if (data.scoringStatus == 27030) {
            scoringStatus = <li className="fa fa-times text-red">
                reject
            </li>;
            joinStatus = '';
        }
        else{
            scoringStatus = 'N/A'
        }


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
    },
    select(id){
        DemoDayActions.selectedIds(id);
    }
});


module.exports = DemoDayConnect;

