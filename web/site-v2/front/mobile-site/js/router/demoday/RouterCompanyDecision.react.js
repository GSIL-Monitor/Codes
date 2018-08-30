var React = require('react');
var Decision = require('../../view/demoday/score/Decision.react');
var HeaderActions = require('../../../../react-kit/action/HeaderActions');

var RouterCompanyDecision = React.createClass({

    componentWillMount() {
        HeaderActions.router('demoDay');
    },

    componentWillReceiveProps(nextProps) {
        HeaderActions.router('demoDay');
    },

    render(){
        var id = this.props.params.id;
        var code = this.props.params.code;
        var type = this.props.params.type;

        return(
            <Decision id={id} code={code}  type={type}/>
        )
    }
});

module.exports = RouterCompanyDecision;
