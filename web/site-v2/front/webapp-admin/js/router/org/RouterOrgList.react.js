var React = require('react');
var OrgList = require('../../view/org/OrgList.react');
var HeaderActions = require('../../../../react-kit/action/HeaderActions');

var RouterOrg = React.createClass({

    componentWillMount() {
        HeaderActions.router('org');
    },

    componentWillReceiveProps(nextProps) {
        HeaderActions.router('org');
    },

    render(){
        return(
            <OrgList />
        )
    }
});

module.exports = RouterOrg;
