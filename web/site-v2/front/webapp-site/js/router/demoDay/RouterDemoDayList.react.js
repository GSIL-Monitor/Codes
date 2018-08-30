var React = require('react');
var DemoDayList = require('../../view/demoDay/DemoDayList.react.js');
var HeaderActions = require('../../../../react-kit/action/HeaderActions');

var RouterDemoDayList = React.createClass({

    componentWillMount() {
        HeaderActions.router('demoDay');
    },

    componentWillReceiveProps(nextProps) {
        HeaderActions.router('demoDay');
    },

    render(){
        return(
            <DemoDayList />
        )
    }
});

module.exports = RouterDemoDayList;
