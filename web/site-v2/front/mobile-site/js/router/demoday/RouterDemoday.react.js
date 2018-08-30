var React = require('react');
var Demoday = require('../../view/demoday/Demoday.react');
var HeaderActions = require('../../../../react-kit/action/HeaderActions');

var RouterDemoDay = React.createClass({

    componentWillMount() {
        HeaderActions.router('demoDay');
    },

    componentWillReceiveProps(nextProps) {
        HeaderActions.router('demoDay');
    },

    render(){
        var id = Number(this.props.params.id);
        return(
            <Demoday id={id}/>
        )
    }
});

module.exports = RouterDemoDay;
