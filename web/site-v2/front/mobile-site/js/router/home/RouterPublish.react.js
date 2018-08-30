var React = require('react');
var Publish = require('../../../../webapp-site/js/view/mytask/Publish.react');

var HeaderActions = require('../../../../react-kit/action/HeaderActions');

var RouterPublish = React.createClass({

    componentWillMount() {
        HeaderActions.router('home');
    },

    componentWillReceiveProps(nextProps) {
        HeaderActions.router('home');
    },

    render(){
        return <Publish  status={this.props.params.status} from="mobile"/>
    }
});

module.exports = RouterPublish;
