var React = require('react');
var Company = require('../view/Company.react.js');
var HeaderActions = require('../../../react-kit/action/HeaderActions');

var RouterCompany = React.createClass({

    componentWillMount() {
        HeaderActions.router('company');
    },

    componentWillReceiveProps(nextProps) {
        HeaderActions.router('company');
    },

    render(){
        var code = this.props.params.code;
        return(
            <Company code={code}/>
        )
    }
});

module.exports = RouterCompany;
