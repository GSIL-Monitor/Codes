var React = require('react');
var Task = require('../../view/mytask/Task.react');

var HeaderActions = require('../../../../react-kit/action/HeaderActions');

var RouterTask = React.createClass({

    componentWillMount() {
        HeaderActions.router('home');
    },

    componentWillReceiveProps(nextProps) {
        HeaderActions.router('home');
    },

    render(){
        return <Task type={this.props.params.type} status={this.props.params.status} />
    }
});

module.exports = RouterTask;
