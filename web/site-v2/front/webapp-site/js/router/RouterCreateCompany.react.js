var React = require('react');
var CreateCompany = require('../view/CreateCompany.react.js');
var HeaderActions = require('../../../react-kit/action/HeaderActions');

var RouterCreateCompany = React.createClass({

    componentWillMount() {
        HeaderActions.router('createCompany');
    },

    componentWillReceiveProps(nextProps) {
        HeaderActions.router('createCompany');
    },

    render(){
        var coldcallId = parseInt(this.props.params.coldcallId);
        var demodayId = parseInt(this.props.params.demodayId);
        return <CreateCompany coldcallId={coldcallId} demodayId={demodayId} />
    }
});

module.exports = RouterCreateCompany;
