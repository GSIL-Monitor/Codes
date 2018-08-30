var React = require('react');
var NewDemoDay = require('../../view/demoDay/NewDemoDay.react');
var HeaderActions = require('../../../../react-kit/action/HeaderActions');

var RouterNewDemoDay = React.createClass({

    componentWillMount() {
        HeaderActions.router('demoDay');
    },

    componentWillReceiveProps(nextProps) {
        HeaderActions.router('demoDay');
    },

    render(){
        return(
            <NewDemoDay />
        )
    }
});

module.exports = RouterNewDemoDay;
