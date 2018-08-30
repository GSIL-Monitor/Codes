var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var DemodayActions = require('../../../../action/DemoDayActions');

const DemoDayOrgList = React.createClass({

    render(){
        var list = this.props.joinList;
        if (!list) {
            return null;
        }
        var me = this;
        return (
            <div>
                <div className="dd-score-list">
                    <div className="preScore-item  dd-list-head">
                        <div className="admin-demoday-org-rank">序号</div>
                        <div >机构名称</div>
                        <div>机构状态</div>
                        <div>移除机构</div>
                        <div>
                            <a className="a-add" onClick={me.add}>
                                <li className="fa  fa-plus m-r-2"/>
                                <span>新增参会机构</span>
                            </a>
                        </div>
                    </div>
                    {list.map(function (result, index) {
                        return <OrgItem key={index}
                                        index={index}
                                        data={result}
                                        onClick={me.click}
                            />
                    })}
                </div>

            </div>
        )

    },
    click(orgId){
        DemodayActions.removeDemodayOrg(orgId);
    },
    add(){
        $('#rejectOrg-modal').show();
    }
});

const OrgItem = React.createClass({

    render(){
        var index = this.props.index + 1;
        var data = this.props.data;
        var status;
        if (data.orgStatus === 31010) {
            status = "X联盟"
        }
        else {
            status = "未知";
        }
        return (
            <div className="preScore-item">
                <div className="admin-demoday-org-rank">{index}</div>
                <div>
                    <a>{data.orgName} </a>
                </div>
                <div> {status}</div>
                <div>
                    <a className="a-add" onClick={this.click}>
                        <i className="fa fa-minus-circle"></i>
                    </a>
                </div>
            </div>
        )
    },
    click(){
        this.props.onClick(this.props.data.orgId);
    }


});


module.exports = DemoDayOrgList;

