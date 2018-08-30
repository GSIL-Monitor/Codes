var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');


var Functions =require('../../../../react-kit/util/Functions');
var DemoDayActions = require('../../action/DemoDayActions');
var DemoDayStore = require('../../store/DemoDayStore');
var ValidateActions = require('../../action/validation/ValidateDemodayActions');
/**** component ***/
var DemodayName=require('./create/DemoDayName.react');
var SubmitEndDate = require('./create/SubmitEndDate.react');
var PreScoreStartDate = require('./create/PreScoreStartDate.react');
var PreScoreEndDate = require('./create/PreScoreEndDate.react');
var ConnectStartDate = require('./create/ConnectStartDate.react');
var ConnectEndDate = require('./create/ConnectEndDate.react');
var HoldStartDate = require('./create/HoldStartDate.react');
var HoldEndDate = require('./create/HoldEndDate.react');
var AddOrgList = require('./form/org/AddOrgList.react');

const NewDemoDay = React.createClass({

    mixins: [Reflux.connect(DemoDayStore, 'data')],

    componentWillMount() {
        DemoDayActions.getOrgList();
    },


    render(){

        if (Functions.isEmptyObject(this.state)) return null;
        var demoday = this.state.data.demoday;
        var orgList = this.state.data.orgList;
        var addOrg;
        if(!Functions.isEmptyObject(this.state)){
            addOrg=  <AddOrgList data={orgList} />;
        }
        var add='添加';
        if(this.state.data.add){
            add='创建中...'
        }

        return(
            <div className="main-body">
                <h3 className="cc-org-title">新建Demo Day</h3>
                <DemodayName  data={demoday.name} onChange={this.onChange} id="demodayName"/>
                <SubmitEndDate data={demoday.submitEndDate}  onChange={this.onChange}  id="submitEndDate"/>
                <PreScoreStartDate data={demoday.preScoreStartDate}  onChange={this.onChange} id="preScoreStartDate" />
                <PreScoreEndDate data={demoday.preScoreEndDate}  onChange={this.onChange}  id="preScoreEndDate" />
                <ConnectStartDate data={demoday.connectStartDate}  onChange={this.onChange} id="connectStartDate"/>
                <ConnectEndDate data={demoday.connectEndDate}  onChange={this.onChange} id="connectEndDate" />
                <HoldStartDate data={demoday.holdStartDate}  onChange={this.onChange} id="holdStartDate"/>
                <HoldEndDate data={demoday.holdEndDate}  onChange={this.onChange}  id="holdEndDate" />
                {addOrg}
                <button className="btn btn-navy cc-org-button" onClick={this.handleAdd}>{add}</button>
            </div>
        )
    },

    onChange(e){
        DemoDayActions.change(e.target.name, e.target.value);
    },

    handleAdd(){
        var demoday = this.state.data.demoday;
        var checkedAdd =true;
        var focused=false;

        if(this.state.data.add){
            checkedAdd=false;
        }
        if(null==demoday.name||demoday.name.trim()==''){
            ValidateActions.name(demoday.name);
            checkedAdd=false;
            if(!focused){
                $("#demodayName").focus();
                focused=true;
            }
        }
        if(null==demoday.submitEndDate||demoday.submitEndDate.trim()==''){
            ValidateActions.date('submitEndDate',demoday.submitEndDate);
            checkedAdd=false;
            if(!focused){
                $("#submitEndDate").focus();
                focused=true;
            }
        }
        if(null==demoday.preScoreStartDate||demoday.preScoreStartDate.trim()==''){
            ValidateActions.date('preScoreStartDate',demoday.preScoreStartDate);
            checkedAdd=false;
            if(!focused){
                $("#preScoreStartDate").focus();
                focused=true;
            }
        }
        if(null==demoday.preScoreEndDate||demoday.preScoreEndDate.trim()==''){
            ValidateActions.date('preScoreEndDate',demoday.preScoreEndDate);
            checkedAdd=false;
            if(!focused){
                $("#preScoreEndDate").focus();
                focused=true;
            }
        }
        if(null==demoday.connectStartDate||demoday.connectStartDate.trim()==''){
            ValidateActions.date('connectStartDate',demoday.connectStartDate);
            checkedAdd=false;
            if(!focused){
                $("#connectStartDate").focus();
                focused=true;
            }
        }
        if(null==demoday.connectEndDate||demoday.connectEndDate.trim()==''){
            ValidateActions.date('connectEndDate',demoday.connectEndDate);
            checkedAdd=false;
            if(!focused){
                $("#connectEndDate").focus();
                focused=true;
            }
        }
        if(null==demoday.holdStartDate||demoday.holdStartDate.trim()==''){
            ValidateActions.date('holdStartDate',demoday.holdStartDate);
            checkedAdd=false;
            if(!focused){
                $("#holdStartDate").focus();
                focused=true;
            }
        }
        if(null==demoday.holdEndDate||demoday.holdEndDate.trim()==''){
            ValidateActions.date('holdEndDate',demoday.holdEndDate);
            checkedAdd=false;
            if(!focused){
                $("#holdEndDate").focus();
                focused=true;
            }
        }
        if(checkedAdd &&!this.state.data.add){
            DemoDayActions.add();
        }
    }

});


module.exports = NewDemoDay;

