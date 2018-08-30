var React = require('react');
var CompleteCompany = require('../../view/demoDay/add/CompleteCompany.react');
var HeaderActions = require('../../../../react-kit/action/HeaderActions');

var RouterCompleteCompany = React.createClass({

    componentWillMount() {
        HeaderActions.router('demoDay');
    },

    componentWillReceiveProps(nextProps) {
        HeaderActions.router('demoDay');
    },

    render(){
        return(
            <CompleteCompany id={this.props.params.id} code={this.props.params.code} />
        )
    }
});

module.exports = RouterCompleteCompany;
