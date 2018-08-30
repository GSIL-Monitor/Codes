var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var DemoDayActions = require('../../../../../action/DemoDayActions');
var DemoDayStore = require('../../../../../store/DemoDayStore');
var DemodayUtil = require('../../../../../util/DemodayUtil');
var Functions = require('../../../../../../../react-kit/util/Functions');
var SelectedList = require('../../../form/FormSelectedList.react.js');

const DemodaySysCompany = React.createClass({

    mixins: [Reflux.connect(DemoDayStore, 'data')],
    componentWillMount(){
        DemoDayActions.getSysCompanies(this.props.demodayId);
    },
    componentWillReceiveProps(nextProps) {
        DemoDayActions.getSysCompanies(nextProps.demodayId);
    },

    render(){

        if (Functions.isEmptyObject(this.state)) return null;
        var demoday = this.state.data.oldDemoday;
        var sysCompanyList = this.state.data.sysCompanyList;
        if (Functions.isEmptyObject(sysCompanyList)) return null;
        var sysCompanyBatch = this.state.data.sysCompanyBatch;
        var rank;
        var operate;
        var demodayId = demoday.id;
        if (sysCompanyBatch) {
            var selectedIds = this.state.data.selectedIds;
            rank = "选中";

            operate = <span>
                        <span className="m-r-20">
                         <input type="checkbox" onChange={this.selectAll} />
                             <span className="m-l-5">
                                全选
                             </span>
                        </span>

                        <a className="cc-text-green m-r-20" onClick={this.pass}>通过</a>
                        <a className="text-red m-r-20" onClick={this.reject}>不通过</a>
                        <a className="text-blue" onClick={this.batchOperateChange}>取消</a>
                    </span>;

        }
        else {
            rank = "序号";
            operate= <a className="text-blue" onClick={this.batchOperateChange}>
                <i className="fa fa-pencil-square-o">更改通过状态</i>
            </a>
        }
        var href = "/admin/#/demoday/"+demoday.id;
        return (
            <div>
                <a href={href} >
                    <h3 className="text-center">{demoday.name}</h3>
                </a>

                <div>
                    <span className="admin-head">
                     <h3>烯牛快跑系统提交项目</h3>
                     </span>
                </div>
                <div className="dd-score-list">
                    <div className="preScore-item  dd-list-head">
                        <div className="admin-demoday-syscomp-rank ">{rank}</div>
                        <div >项目名称</div>
                        <div>提交日期</div>
                        <div>是否通过</div>
                        <div>
                            {operate}
                        </div>
                    </div>
                    {sysCompanyList.map(function (result, index) {
                        return <CompanyItem key={index} data={result} index={index}
                                            batchOperate={sysCompanyBatch}
                                            selectedIds={selectedIds}
                                            demodayId={demodayId}
                            />
                    })

                    }
                </div>


            </div>
        )
    },

    batchOperateChange(){
        DemoDayActions.sysCompanyBatch();
    },

    pass(){
        DemoDayActions.sysCompanyBatchOperate('Y',this.state.data.oldDemoday.id);
    },
    reject(){
        DemoDayActions.sysCompanyBatchOperate('N',this.state.data.oldDemoday.id);
    },
    selectAll(){
        DemoDayActions.selectSysCompAll();
    }
});


const CompanyItem = React.createClass({

    render(){


        var index;
        var batchOperate = this.props.batchOperate;
        var data = this.props.data;
        var time= data.createTime;
        var createTime = new Date(time).format("yyyy-MM-dd hh:mm:ss");
        var pass;
        if(data.pass=='Y'){
          pass=<span className="cc-text-green">是</span>
        }
        else{
            pass=<span className="text-red">否</span>
        }

        var href = "/#/demoday/"+this.props.demodayId+"/company/"+data.code+"/preScore";
        if (batchOperate) {
            index = <SelectedList selectedIds={this.props.selectedIds} id={data.id}
                                  select={this.select}/>;
        }
        else {
            index = this.props.index + 1;
        }
        return (

            <div className="preScore-item">
                <div className="admin-demoday-syscomp-rank">{index}</div>
                <div><a href={href}>{data.name}</a></div>
                <div>{createTime.substring(0,10)}</div>
                <div>
                    {pass}
                </div>


            </div>
        )

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
module.exports = DemodaySysCompany;

