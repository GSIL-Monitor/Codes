var React = require('react');
var CollectionDetail = require('../../view/collection/CollectionDetail.react');
var HeaderActions = require('../../../../react-kit/action/HeaderActions');

var RouterCollection = React.createClass({

    componentWillMount() {
        HeaderActions.router('collection');
    },

    componentWillReceiveProps(nextProps) {
        HeaderActions.router('collection');
    },

    render(){
        var collectionId = Number(this.props.params.collectionId);
        return(
            <CollectionDetail collectionId={collectionId}/>
        )
    }
});

module.exports = RouterCollection;
