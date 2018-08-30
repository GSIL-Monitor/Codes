var React = require('react');
var NewCollection = require('../../view/collection/new/NewCollection.react');
var HeaderActions = require('../../../../react-kit/action/HeaderActions');

var RouterCollection = React.createClass({

    componentWillMount() {
        HeaderActions.router('newCollection');
    },

    componentWillReceiveProps(nextProps) {
        HeaderActions.router('newCollection');
    },

    render(){
        return(
            <NewCollection />
        )
    }
});

module.exports = RouterCollection;
