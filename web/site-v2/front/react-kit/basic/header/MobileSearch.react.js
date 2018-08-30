var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var HeaderActions = require('../../action/HeaderActions');

var MobileSearchBar = require('../search/MobileSearchBar.react');

var MobileSearch = React.createClass({

    render(){
        var data = this.props.data;

        //<div className="m-header-close" onClick={this.searchClose}>
        //    <i className="fa fa-times fa-lg"></i>
        //</div>

        return (
                <MobileSearchBar value={data.search}/>
        )
    },

    searchClose(){
        //$('.page-wrapper, footer').show();
        HeaderActions.clickSearchClose();
    }
});

module.exports = MobileSearch;