var React = require('react');
var HeaderActions = require('../../../react-kit/action/HeaderActions');
var Recommendation = require('../view/Recommendation.react');

var RouterRecommendation = React.createClass({

    componentWillMount() {
        HeaderActions.router('recommend');
    },

    componentWillReceiveProps(nextProps) {
        HeaderActions.router('recommend');
    },

    render(){
        return(
            <Recommendation />
        )
    }
});

module.exports = RouterRecommendation;
