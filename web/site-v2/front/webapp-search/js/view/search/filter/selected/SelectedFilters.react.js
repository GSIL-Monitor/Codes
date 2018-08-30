var React = require('react');

var SelectedFilterDates = require('./SelectedFilterDates.react');
var SelectedFilterLocations = require('./SelectedFilterLocations.react');
var SelectedFilterRounds = require('./SelectedFilterRounds.react');
var SelectedFilterSectors = require('./SelectedFilterSectors.react');


const SelectedFilters = React.createClass({
    render(){
        var data = this.props.data;
        if( data.filterSectors.length   == 0 &&
            data.filterRounds.length    == 0 &&
            data.filterLocations.length == 0 &&
            data.filterDates.length     == 0 ){
            return null;
        }

        return(
            <div className="search-selected-filters">
                <SelectedFilterSectors data={data}/>
                <SelectedFilterRounds data={data}/>
                <SelectedFilterLocations data={data}/>
                <SelectedFilterDates data={data}/>
            </div>
        )
    }
});

module.exports = SelectedFilters;