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
        var demodayId = parseInt(this.props.params.demodayId);
        return(
            <DemoDay  demodayId={demodayId}/>
        )
    }
});

module.exports = RouterDemoDay;
