var React = require('react');
var DemoDay = require('../../view/demoDay/DemoDay.react');
var HeaderActions = require('../../../../react-kit/action/HeaderActions');

var RouterDemoDay = React.createClass({

    componentWillMount() {
        HeaderActions.router('demoDay');
    },

    componentWillReceiveProps(nextProps) {
        HeaderActions.router('demoDay');
    },

    render(){
        return(
            <DemoDay id={this.props.params.id} />
        )
    }
});

module.exports = RouterDemoDay;
