var React = require('react');
var $ = require('jquery');

var Functions = require('../../../../../react-kit/util/Functions');
var CommonSearchActions = require('../../../../../react-kit/action/SearchActions');

var SearchActions = require('../../../action/SearchActions');
var SearchUitl = require('../../../util/SearchUtil');


const FilterSector = React.createClass({

    //<div className="filter-more-search">
    //    <input type="text"
    //           className="filter-search-input"
    //           placeholder="更多领域" />
    //</div>

    render(){
        var data = this.props.data;
        var select = data.sectors;
        var filter = data.filterSectors;
        if(select == null) return null;
        if(select.length == 0) return null;

        var from = this.props.from;

        return(
            <div className="span-select-list">
                <h4 className="filter-head">领域</h4>

                { select.map(function(result, index){
                    return  <SectorItem key={index} data={result} filter={filter} from={from}/>
                }.bind(this))}

            </div>
        )
    },

    click(){
        $('#date-modal').show();
    }

});


const SectorItem = React.createClass({

    render(){
        var selectClass = "select-span sector-span ";
        if(SearchUitl.isInList(this.props.data.id, this.props.filter)){
            selectClass += 'filter-selected';
        }

        return  <span className={selectClass} onClick={this.handleClick}>
                     {this.props.data.sectorName}
                </span>
    },

    handleClick(){
        SearchActions.filterSector(this.props.data.id, this.props.from);
    }
});


module.exports = FilterSector;