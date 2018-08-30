var React = require('react');

var HeaderActions = require('../../../../react-kit/action/HeaderActions');

var DemoDaySysCompany = require('../../view/demoDay/basic/demodayCompany/sysCompany/DemodaySysCompany.react');

var RouterDemodaySysCompany = React.createClass({

    componentWillMount() {
        HeaderActions.router('demoDay');
    },

    componentWillReceiveProps(nextProps) {
        HeaderActions.router('demoDay');
    },

    render(){
        var demodayId = parseInt(this.props.params.demodayId);
        return (
            <DemoDaySysCompany demodayId={demodayId}/>
        )
    }
});

module.exports = RouterDemodaySysCompany;
