var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');
var Functions = require('../../../../../../react-kit/util/Functions');
var DemoDayActions = require('../../../../action/DemoDayActions');
var DemodayStore = require('../../../../store/DemoDayStore');

var RejectOrgSelect = require('./../../form/org/RejectOrgSelect.react.js');
var DemodayUtil = require('../../../../util/DemodayUtil');

const RejectOrgList = React.createClass({
    mixins: [Reflux.connect(DemodayStore, 'data')],

    render(){
        var state = this.state;
        if (Functions.isEmptyObject(state))
            return null;
        var rejectOrgs = this.state.data.rejectOrgs;
        var addOrgIds= this.state.data.addOrgIds;
        if (Functions.isEmptyObject(rejectOrgs)) return null;
        var add = '添加';
        var className = "btn btn-navy cc-org-button";
        if (DemodayUtil.orgSelected(addOrgIds)) {
            className = "btn btn-navy cc-org-button";
        }
        else {
            className += " un-change";
        }

        return (
            <div>
            <RejectOrgSelect data={rejectOrgs} addOrgIds={addOrgIds}/>
                <button className={className} onClick={this.handleUpdate}>{add}</button>
            </div>

        )

    },
    handleUpdate(){
        DemoDayActions.addDemodayOrgs();
        $('#rejectOrg-modal').hide();
    }
});
module.exports = RejectOrgList;


