var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var OrgStore = require('../../store/OrgStore');
var OrgActions = require('../../action/OrgActions');
var ValidateActions = require('../../action/validation/ValidateOrgActions');
var Functions =require('../../../../react-kit/util/Functions');

var OrgName = require('./form/OrgName.react');
var OrgStatus = require('./form/OrgStatus.react');
const NewOrg = React.createClass({

    mixins: [Reflux.connect(OrgStore, 'data')],

    componentWillMount() {
        OrgActions.getInitData();
    },


    render(){
        if (Functions.isEmptyObject(this.state)) return null;
        var org = this.state.data.org;
        var name = org.name;
        var status = org.status;
        var add='添加';
        if(this.state.data.add){
            add='创建中...'
        }

        return(
            <div className="main-body">
                 <h3 className="cc-org-title">新建机构</h3>
                <OrgName  data={name} onChange={this.onChange} id="orgName"/>
                <OrgStatus data={status} onChange={this.onChange} />
                <button className="btn btn-navy cc-org-button" onClick={this.handleAdd}>{add}</button>
            </div>
        )
    },
    onChange(e){
        OrgActions.change(e.target.name, e.target.value);
    },
    handleAdd(){
        var name = this.state.data.org.name;
        var checkedAdd =true;
        var focused=false;

        if(this.state.data.add){
            checkedAdd=false;
        }
        if(name.trim()==''){
            ValidateActions.name(name);
            checkedAdd=false;
            if(!focused){
                $("#orgName").focus();
                focused=true;
            }
        }
        if(checkedAdd &&!this.state.data.add){
            OrgActions.add();
        }
    }

});


module.exports = NewOrg;

