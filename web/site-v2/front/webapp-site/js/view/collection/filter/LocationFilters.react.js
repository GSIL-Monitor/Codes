var React = require('react');
var CollectionForm = require('./CollectionForm.react.js');

const LocationFilters = React.createClass({

    render(){
        var data = this.props.data;
        var selected = data.selectedLocations;
        var list = data.locations;

        var from = this.props.from;
        return(
            <CollectionForm label='地区' list={list} type='location' selected={selected} from={from}/>
        )
    }

});

module.exports = LocationFilters;