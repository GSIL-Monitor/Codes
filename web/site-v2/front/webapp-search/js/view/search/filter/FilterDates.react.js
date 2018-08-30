var React = require('react');
var $ = require('jquery');

var Functions = require('../../../../../react-kit/util/Functions');
var CommonSearchActions = require('../../../../../react-kit/action/SearchActions');

var SearchActions = require('../../../action/SearchActions');
var SearchUitl = require('../../../util/SearchUtil');

const FilterDates = React.createClass({

    render(){
        var dateSelect = Functions.dateSelect();
        var data = this.props.data;
        var from = this.props.from;

        //<a className="a-more" onClick={this.click}>具体时间</a>
        return(
            <div className="span-select-list">
                <h4 className="filter-head">创立时间</h4>

                { dateSelect.map(function(result, index){
                    return  <DateItem key={index} data={result} filter={data.filterDates} from={from}/>
                }.bind(this))}
            </div>
        )
    },

    click(){
        $('#date-modal').show();
    }

});


const DateItem = React.createClass({

    render(){
        var selectClass = "select-span ";
        var state = this.state;
        if(SearchUitl.isInList(this.props.data, this.props.filter)){
            selectClass += 'filter-selected';
        }

        return  <span className={selectClass} onClick={this.handleClick}>
                     {this.props.data}
                </span>
    },

    handleClick(){
        SearchActions.filterDate(this.props.data, this.props.from);
    }
});


module.exports = FilterDates;