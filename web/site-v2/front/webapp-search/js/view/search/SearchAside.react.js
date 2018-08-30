var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Functions = require('../../../../react-kit/util/Functions');
var BasicSearchActions = require('../../../../react-kit/action/SearchActions');

var FilterSectors = require('./filter/FilterSectors.react');
var FilterRounds = require('./filter/FilterRounds.react');
var FilterLocations = require('./filter/FilterLocations.react');
var FilterDates = require('./filter/FilterDates.react');

var SearchStore = require('../../store/SearchStore');
var SearchActions = require('../../action/SearchActions');

const SearchAside = React.createClass({

    render(){
        var data = this.props.data;
        var search = data.search;

        var cleanFilter;
        if( data.filterSectors.length    > 0 ||
            data.filterRounds.length     > 0 ||
            data.filterLocations.length  > 0 ||
            data.filterDates.length      > 0 ){
            cleanFilter = <a className="clean-filter" onClick={this.cleanFilter}>清空</a>
        }

        return(
            <div className="column  one-fourth">
                <div className="m-t-20 m-r-30">
                    <div className="filter-title">过滤条件</div>
                    {cleanFilter}

                    <Filter data={data}/>
                </div>
            </div>
        )
    },

    cleanFilter(){
        SearchActions.cleanFilters();
    }
});



const Filter = React.createClass({

    render(){

        //<div className="more-filter">
        //    <a>更多过滤</a>
        //</div>

        var data = this.props.data;

        return(
            <div>
                <FilterSectors data={data} />
                <FilterRounds data={data} />
                <FilterLocations data={data} />
                <FilterDates data={data} />
            </div>
        )
    }
});






module.exports = SearchAside;
