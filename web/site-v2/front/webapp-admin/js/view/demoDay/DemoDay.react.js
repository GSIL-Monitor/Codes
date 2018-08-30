var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Functions = require('../../../../react-kit/util/Functions');

var DemoDayActions = require('../../action/DemoDayActions');
var DemoDayStore = require('../../store/DemoDayStore');
var DemodayUtil = require('../../util/DemodayUtil');

var DemoDayBasic = require('./basic/DemoDayBasic.react');
var DemoDayOrgBasic = require('./basic/DemoDayOrgBasic.react');
var DemoDayCompanyBasic = require('./basic/DemodayCompanyBasic.react');

const DemoDay = React.createClass({

    mixins: [Reflux.connect(DemoDayStore, 'data')],
    componentWillMount(){
        DemoDayActions.getInitData(this.props.demodayId);
    },
    componentWillReceiveProps(nextProps) {
        DemoDayActions.getInitData(nextProps.demodayId);
    },

    render(){
        if (Functions.isEmptyObject(this.state)) return null;
        var demodayId = this.state.data.demodayId;
        var oldDemoday = this.state.data.oldDemoday;
        if(Functions.isEmptyObject(oldDemoday)) return null;
        var newDemoday = this.state.data.newDemoday;
        var joinOrgs = this.state.data.joinOrgs;
        var demodayCompanies = this.state.data.demodayCompanies;

        var updateDemoday = this.state.data.updateDemoday;
        var updateCompany = this.state.data.updateCompany;
        var selectedIds = this.state.data.selectedIds;
        var strDates = this.state.data.strDates;
        var link="/admin/#/demoday/"+demodayId+"/sys/company";
        return (
            <div className="main-body">
                <DemoDayBasic oldDemoday={oldDemoday}
                              newDemoday={newDemoday}
                              updateDemoday={updateDemoday}
                              onUpdate={this.update}
                              onChange={this.onChange}
                              confirm={this.updateDemoday}
                              demodayId={demodayId}
                              strDates={strDates}
                              link={link}
                    />
                <DemoDayOrgBasic joinList={joinOrgs}/>
                <DemoDayCompanyBasic demodayCompanies={demodayCompanies}
                                     updateCompany={updateCompany}
                                     onUpdate={this.update}
                                     updateCompanyStatus={this.updateCompanyStatus}
                                     updateStatus={this.updateStatus}
                                     demodayStatus={oldDemoday.status}
                                     demodayId={demodayId}
                                     selectedIds={selectedIds}
                    />
            </div>
        )
    },

    update(value){
        DemoDayActions.update(value);
    },

    updateDemoday(){
        DemoDayActions.updateDemoday();
    },

    onChange(e,date){
        DemoDayActions.change(e.target.name, e.target.value, true,date);
    },

    updateCompanyStatus(){
        DemoDayActions.updateCompanyStatus();
    },
    updateStatus(e, code){
        DemoDayActions.updateStatus(e.target.name, e.target.value, code);
    }

});


module.exports = DemoDay;

