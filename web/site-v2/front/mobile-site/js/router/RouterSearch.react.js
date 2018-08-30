var React = require('react');
var Search = require('../../../webapp-search/js/view/search/MobileSearch.react');
var HeaderActions = require('../../../react-kit/action/HeaderActions');

var RouterSearch = React.createClass({

    componentWillMount() {
        HeaderActions.initSearch(this.props.params.value);
    },

    componentWillReceiveProps(nextProps) {
        if(this.props.params.value == nextProps.params.value) return;
        HeaderActions.initSearch(nextProps.params.value);
    },


    render(){
        return(
            <Search value={this.props.params.value} />
        )
    }
});

module.exports = RouterSearch;
