var React = require('react');
var Reflux = require('reflux');


var DemoDayOrgList = require('../form/org/DemodayOrgList.react');

const DemoDayOrgBasic = React.createClass({

    render(){
        var joinList = this.props.joinList;
        return (
            <div className="m-t-20" >
                   <h3>参会机构</h3>

                <DemoDayOrgList joinList={joinList} />
            </div>
        )
    }
});

module.exports = DemoDayOrgBasic;

