var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');
var Functions = require('../../../../../../react-kit/util/Functions');

var DemoDayActions = require('../../../../action/DemoDayActions');
var DemoDayStore = require('../../../../store/DemoDayStore');

const RejectOrgSelect = React.createClass({


    render(){
        var orgList = this.props.data;
        var me =this;
        return (
            <div>
                {orgList.map(function (result,index) {
                    return <OrgItem key={index} data={result} addOrgIds={me.props.addOrgIds}/>
                })}
            </div>
        )
    },

});


const OrgItem = React.createClass({


    render(){
        var org = this.props.data;
        var name = org.orgName;
        var list = this.props.addOrgIds;

        var flag;
        if (list.length > 0) {
            for (var i in list) {
                if (org.orgId == list[i].id) {
                    if (list[i].selected)
                        flag = true;
                }
            }
        }

        var className = 'product-select ';
        if (flag) className += 'product-selected';
        return (
            <div className="new-org-item">
                <div className="org-item-info">
                    <div className={className} onClick={this.click}></div>
                    <span>{name}</span>
                </div>

            </div>
        )
    },

    click(){
        DemoDayActions.selectOrg(this.props.data.orgId);

    }
});

module.exports = RejectOrgSelect;