var React = require('react');
var Discovery = require('../../view/mytask/Discovery.react');

var HeaderActions = require('../../../../react-kit/action/HeaderActions');

var RouterDiscovery = React.createClass({

    componentWillMount() {
        HeaderActions.router('home');
    },

    componentWillReceiveProps(nextProps) {
        HeaderActions.router('home');
    },

    render(){
        return <Discovery  status={this.props.params.status} />
    }
});

module.exports = RouterDiscovery;
