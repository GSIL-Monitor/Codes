var React = require('react');
var Search = require('../view/search/Search.react.js');

var RouterSearch = React.createClass({

    render(){
        return(
            <Search value={this.props.params.value} type={this.props.params.type} />
        )
    }
});

module.exports = RouterSearch;
