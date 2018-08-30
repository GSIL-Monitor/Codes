var React = require('react');
var CompanyScore = require('../../view/demoday/score/CompanyScore.react');
var HeaderActions = require('../../../../react-kit/action/HeaderActions');

var RouterCompanyScore = React.createClass({

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
            <CompanyScore id={id} code={code} type={type}/>
        )
    }
});

module.exports = RouterCompanyScore;
