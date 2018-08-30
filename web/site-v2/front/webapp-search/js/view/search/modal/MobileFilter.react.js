var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Functions = require('../../../../../react-kit/util/Functions');
var BasicSearchActions = require('../../../../../react-kit/action/SearchActions');

var FilterSectors = require('../filter/FilterSectors.react');
var FilterRounds = require('../filter/FilterRounds.react');
var FilterLocations = require('../filter/FilterLocations.react');
var FilterDates = require('../filter/FilterDates.react');

var SearchStore = require('../../../store/SearchStore');
var SearchActions = require('../../../action/SearchActions');

const MobileFilter = React.createClass({

    render(){
        var data = this.props.data;
        var search = data.search;

        //var cleanFilter;
        //if( data.filterSectors.length    > 0 ||
        //    data.filterRounds.length     > 0 ||
        //    data.filterLocations.length  > 0 ||
        //    data.filterDates.length      > 0 ){
        //    cleanFilter = <a className="clean-filter" onClick={this.cleanFilter}>清空</a>
        //}

        return(
                <div className="search-filters">
                    <Filter data={data}/>
                </div>
        )
    },

    cleanFilter(){
        SearchActions.cleanFilter();
    }
});



const Filter = React.createClass({

    render(){
        var data = this.props.data;
        return(
            <div>
                <FilterSectors data={data} from="mobile"/>
                <FilterRounds data={data} from="mobile"/>
                <FilterLocations data={data} from="mobile"/>
                <FilterDates data={data} from="mobile"/>

                <div className="text-right">
                    <button className="btn btn-navy m-r-10" onClick={this.comfirm}>确认</button>
                    <button className="btn btn-gray" onClick={this.cancel}>(清空)取消</button>
                </div>
            </div>
        )
    },

    comfirm(){
       SearchActions.comfirmFilters();
    },

    cancel(){
        SearchActions.cancelFilters();
        $('.modal').hide();
    }


});

module.exports = MobileFilter;
