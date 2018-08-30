var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var DemoDayActions = require('../../action/DemoDayActions');
var DemoDayStore = require('../../store/DemoDayStore');
var DemodayUtil = require('../../util/DemodayUtil');
var Functions = require('../../../../react-kit/util/Functions');
var SelectedList = require('./form/FormSelectedList.react.js');

const DemoDayPreScores = React.createClass({

    mixins: [Reflux.connect(DemoDayStore, 'data')],
    componentWillMount(){
        DemoDayActions.getPreScores(this.props.demodayId);
    },
    componentWillReceiveProps(nextProps) {
        DemoDayActions.getPreScores(nextProps.demodayId);
    },

    render(){

        if (Functions.isEmptyObject(this.state)) return null;
        var demoday = this.state.data.oldDemoday;
        var preScores = this.state.data.preScores;
        if (Functions.isEmptyObject(preScores)) return null;
        var me = this;
        var batchOperate = this.state.data.batchOperate;
        var rank;
        var operate;
        if (batchOperate) {
            var selectedIds = this.state.data.selectedIds;
            rank = "选中";
            operate = <span>
                        <a className="cc-text-green m-r-20" onClick={this.pass}>pass</a>
                        <a className="text-red m-r-20" onClick={this.reject}>reject</a>
                        <a className="text-blue" onClick={this.batchOperateChange}>取消</a>
                    </span>;
        }
        else {
            rank = "序号";
            operate = <span>
                         <a className="text-blue" onClick={this.batchOperateChange}>
                             <i className="fa fa-pencil-square-o">批量操作</i>
                         </a>
                    </span>;
        }
        var href = "/admin/#/demoday/"+demoday.id;
        return (
            <div>
                <a href={href} >
                <h3 className="text-center">{demoday.name}</h3>
                    </a>

                <div>
                    <span className="admin-head">
                     <h3> 初筛打分信息</h3>
                     </span>
                    {operate}
                </div>
                <div className="dd-score-list">
                    <div className="preScore-item  dd-list-head">
                        <div className="admin-demoday-prescore-rank ">{rank}</div>
                        <div >项目名称</div>
                        <div>平均分</div>
                        <div>合伙人打分</div>
                        <div>所有打分</div>
                        <div>操作</div>
                        <div>初筛状态</div>
                    </div>
                    {preScores.map(function (result, index) {
                        return <CompanyItem key={index} data={result}
                                            index={index}
                                            allPreScores={me.allPreScores}
                                            batchOperate={batchOperate}
                                            selectedIds={selectedIds}
                            />
                    })

                    }
                </div>


            </div>
        )
    },
    allPreScores(dealDemodayId){
        DemoDayActions.allPreScores(dealDemodayId);
    },

    batchOperateChange(){
        DemoDayActions.batchOperateChange();
    },

    pass(){
        DemoDayActions.batchOperate(27020);
    },
    reject(){
        DemoDayActions.batchOperate(27030);
    }
});


const CompanyItem = React.createClass({

    render(){

        var avg = '0';
        var avgPreScore = this.props.data;
        if (avgPreScore.avg) {
            avg = avgPreScore.avg;
        }
        var index;
        var batchOperate = this.props.batchOperate;

        if (batchOperate) {
            index = <SelectedList selectedIds={this.props.selectedIds} id={avgPreScore.demodayCompanyId}
                select={this.select}/>
        }
        else {
            index = this.props.index + 1;
        }

        var partnerPreScores = avgPreScore.partnerPreScores;
        var preScore;
        if (partnerPreScores == null || partnerPreScores.length == 0) {
            preScore = '尚未打分'
        }
        else {

            preScore = <div className="admin-partner-prescore">
                {
                    partnerPreScores.map(function (result, index) {
                        return <PartnerItem key={index} data={result}
                            />

                    })
                }

            </div>
        }
        var scoringStatus = avgPreScore.scoringStatus;
        var operate;
        if (scoringStatus == 27010||scoringStatus==null) {
            scoringStatus = '';
            operate = <div>
                        <span className="m-r-10"><a className="cc-text-green" onClick={this.pass}>pass</a></span>
                         <span ><a className="text-red" onClick={this.reject}>reject</a></span>
                     </div>


        } else if (scoringStatus == 27020) {
            scoringStatus =
                <li className="fa fa-check cc-text-green">pass</li>;
            operate = <div>
                        <span ><a className="text-red" onClick={this.reject}>reject</a></span>
                      </div>
        }
        else if (scoringStatus == 27030) {
            scoringStatus = <li className="fa fa-times text-red">
                            reject
                            </li>;
            operate = <div>
                        <span ><a className="cc-text-green" onClick={this.pass}>pass</a></span>
                      </div>
        }
        return (

            <div className="preScore-item">
                <div className="admin-demoday-prescore-rank">{index}</div>
                <div>{avgPreScore.name}</div>
                <div>{avg}</div>
                <div >
                    {preScore}
                </div>
                <div>
                    <a onClick={this.handleClick}>
                        <li className="fa fa-angle-double-right"/>
                    </a>
                </div>
                {operate}
                <div>{scoringStatus}</div>
            </div>
        )

    },
    handleClick(){
        this.props.allPreScores(this.props.data.demodayCompanyId);
        $("#preScores").show();
    },
    pass(){
        DemoDayActions.preScoreResult(this.props.data.demodayCompanyId, 27020);
    },
    reject(){
        DemoDayActions.preScoreResult(this.props.data.demodayCompanyId, 27030);
    },

    select(id){
        DemoDayActions.selectedIds(id);
    }

});


const PartnerItem = React.createClass({
    render(){

        var partnerPreScore = this.props.data;
        var preScore;
        var userName;
        if (partnerPreScore.score == null) {
            userName = '';
            preScore = '';
        }
        else {
            userName = partnerPreScore.userName;
            preScore = partnerPreScore.score;
        }


        return (
            <span className="m-r-10">
                    <span >
                      {userName}
                    </span>
                     <span className="m-l-10">
                         {preScore}
                    </span>
                </span>

        )
    }
});

module.exports = DemoDayPreScores;

