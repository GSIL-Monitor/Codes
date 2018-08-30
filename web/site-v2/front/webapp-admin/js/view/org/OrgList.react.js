var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var OrgStore = require('../../store/OrgStore');
var OrgActions = require('../../action/OrgActions');
var Functions = require('../../../../react-kit/util/Functions');
var FormSelect = require('../demoDay/form/FormSelect.react');
var DemodayUtil = require('../../util/DemodayUtil')


const OrgList = React.createClass({

    mixins: [Reflux.connect(OrgStore, 'data')],

    componentWillMount() {
        OrgActions.getInitData();
    },
    render(){
        var state = this.state;
        if (Functions.isEmptyObject(state))
            return null;
        var orgList = this.state.data.orgList;
        var updateOrg=this.state.data.updateOrg;
        if(!orgList) return null;
        var modifyId = this.state.data.modifyId;
        return (
            <div>
                <div><button className="btn btn-navy" onClick={this.create}>新建</button></div>
                <div className="dd-score-list">
                    <div className="preScore-item  dd-list-head">
                        <div className="preScore-item-rank">序号</div>
                        <div>机构名称</div>
                        <div>机构状态</div>
                        <div>机构功能</div>
                        <div>创建时间</div>
                        <div>修改</div>
                    </div>
                    {orgList.map(function(result, index){
                        return <OrgItem key={index}
                                             index={index}
                                             data={result}
                                             updateOrg={updateOrg}
                                             modifyId={modifyId}
                                             />
                    })}
                </div>

            </div>
        )

    },

    create(){
        window.location.href="/admin/#/new/org";
    }

});

const OrgItem=React.createClass({

    render(){
        var index = this.props.index + 1;
        var data = this.props.data;
        var status;
        if(data.status===31010){
            status="X联盟"
        }
        else{
            status="未知";
        }
        var grade;
        if(data.grade==33010){
            grade="全功能"
        }
        else if(data.grade==33020){
            grade="部分功能"
        }
        var time= data.createTime;
        var createTime = new Date(time).format("yyyy-MM-dd hh:mm:ss");

        if(this.props.modifyId==data.id){
            data = this.props.updateOrg;
            if(data==null) return null;
            var select= DemodayUtil.orgGrade;
            gradeSelect=<FormSelect select={select} onChange={this.onChange} name="grade" value={data.grade} />
            return(
                <div className="preScore-item">
                    <div className="preScore-item-rank">{index}</div>
                    <div>
                        <input type="text"
                               name="name"
                               value={data.name}
                               onChange={this.onChange}
                            />
                    </div>
                    <div>{status}</div>
                    <div>{gradeSelect}</div>
                    <div>{createTime.substring(0,10)}</div>
                    <a onClick={this.confirm}>确定</a>
                    <a  className="m-l-40" onClick={this.cancel}>取消</a>
                </div>
            )


        }
        else{
            var href="/admin/#/org/"+data.id+"/user";
            return(
                <div className="preScore-item">
                    <div className="preScore-item-rank">{index}</div>
                    <div>
                        <a href={href}> {data.name} </a>
                    </div>
                    <div>{status}</div>
                    <div>{grade}</div>
                    <div>{createTime.substring(0,10)}</div>
                    <div>
                    <a  onClick={this.modify}>
                        <i className="fa fa-pencil-square-o" />
                    </a>
                        </div>
                </div>
            )
        }


    },

    onChange(e){
        OrgActions.updateOrg(e.target.name,e.target.value);
    },

    modify(){
        OrgActions.modify(this.props.data.id,this.props.data);
    },
    cancel(){
        OrgActions.cancel();
    },

    delete(){
        OrgActions.deleteOrg(this.props.data.id)
    },

    confirm(){
        OrgActions.confirm();
    }


});

module.exports = OrgList;

