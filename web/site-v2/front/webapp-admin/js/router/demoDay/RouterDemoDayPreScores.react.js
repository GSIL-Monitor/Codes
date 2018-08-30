var React = require('react');

var HeaderActions = require('../../../../react-kit/action/HeaderActions');

var DemoDayPreScores = require('../../view/demoDay/DemoDayPreScores.react');

var RouterDemoDayPreScores = React.createClass({

    componentWillMount() {
        HeaderActions.router('demoDay');
    },

    componentWillReceiveProps(nextProps) {
        HeaderActions.router('demoDay');
    },

    render(){
        var demodayId = parseInt(this.props.params.demodayId);
        return(
            <DemoDayPreScores demodayId={demodayId} />
        )
    }
});

module.exports = RouterDemoDayPreScores;
