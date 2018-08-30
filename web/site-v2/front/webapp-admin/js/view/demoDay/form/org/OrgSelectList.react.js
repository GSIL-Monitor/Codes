var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');
var Functions = require('../../../../../../react-kit/util/Functions');

var DemoDayActions = require('../../../../action/DemoDayActions');
var DemoDayStore = require('../../../../store/DemoDayStore');

const OrgSelectList = React.createClass({


    render(){
        var orgList = this.props.data;
        return (
            <div>
                {orgList.map(function (result) {
                    return <OrgItem key={result.id} data={result}/>
                })}
            </div>
        )
    },

});


const OrgItem = React.createClass({

    mixins: [Reflux.connect(DemoDayStore, 'data')],

    render(){
        var org = this.props.data;
        var name = org.name;
        var list = [];
        if (!Functions.isEmptyObject(this.state)) {
            list = this.state.data.addOrgIds;
        }
        var flag;
        if (list.length > 0) {
            for (var i in list) {
                if (org.id == list[i].id) {
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
        DemoDayActions.selectOrg(this.props.data.id);

    },
});

module.exports = OrgSelectList;