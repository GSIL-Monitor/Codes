var React = require('react');
var Collection = require('../../view/collection/Collection.react');
var HeaderActions = require('../../../../react-kit/action/HeaderActions');

var RouterCollection = React.createClass({

    componentWillMount() {
        HeaderActions.router('collection');
    },

    componentWillReceiveProps(nextProps) {
        HeaderActions.router('collection');
    },

    render(){
        return(
            <Collection />
        )
    }
});

module.exports = RouterCollection;
