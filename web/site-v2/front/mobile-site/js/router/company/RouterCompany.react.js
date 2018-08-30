var React = require('react');
var Company = require('../../view/Company.react');
var HeaderActions = require('../../../../react-kit/action/HeaderActions');

var RouterCompany = React.createClass({

    componentWillMount() {
        HeaderActions.router('company');
    },

    componentWillReceiveProps(nextProps) {
        HeaderActions.router('company');
    },

    render(){
        return(
            <Company code={this.props.params.code}/>
        )
    }
});

module.exports = RouterCompany;
