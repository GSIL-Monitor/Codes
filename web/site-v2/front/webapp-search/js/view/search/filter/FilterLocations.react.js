var React = require('react');
var $ = require('jquery');

var Functions = require('../../../../../react-kit/util/Functions');
var CommonSearchActions = require('../../../../../react-kit/action/SearchActions');

var SearchActions = require('../../../action/SearchActions');
var SearchUitl = require('../../../util/SearchUtil');

var LocationInput = require('../../../../../react-kit/basic/search/LocationInput.react');

const FilterLocation = React.createClass({

    //<div className="filter-more-search">
    //    <LocationInput  className = "filter-search-input"
    //                    placeholder="更多地区"
    //                    value=""
    //                    id=""
    //                    from="filterLocation" />
    //</div>

    render(){
        var locationSelect = Functions.locationUseful();
        var data= this.props.data;
        var filter = data.filterLocations;
        var from = this.props.from;

        return(
            <div className="span-select-list">
                <h4 className="filter-head">地区</h4>

                { locationSelect.map(function(result, index){
                    return <LocationItem key={index} data={result} filter={filter} from={from}/>
                }.bind(this))}


            </div>
        )
    }
});


const LocationItem = React.createClass({

    render(){
        var selectClass = "select-span ";
        var state = this.state;
        if(SearchUitl.isInList(this.props.data.value, this.props.filter)){
            selectClass += 'filter-selected';
        }

        return  <span className={selectClass} onClick={this.handleClick}>
                            {this.props.data.name}
                </span>;
    },

    handleClick(){
        SearchActions.filterLocation(this.props.data.value, this.props.from);
    }
});



module.exports = FilterLocation;