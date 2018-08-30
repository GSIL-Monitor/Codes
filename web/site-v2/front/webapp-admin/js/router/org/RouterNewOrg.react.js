var React = require('react');
var NewOrg = require('../../view/org/NewOrg.react');
var HeaderActions = require('../../../../react-kit/action/HeaderActions');

var RouterNewOrg = React.createClass({

    componentWillMount() {
        HeaderActions.router('org');
    },

    componentWillReceiveProps(nextProps) {
        HeaderActions.router('org');
    },

    render(){
        return(
            <NewOrg />
        )
    }
});

module.exports = RouterNewOrg;
