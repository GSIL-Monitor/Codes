var React = require('react');
var Functions = require('../../../../../../react-kit/util/Functions');
var SearchActions = require('../../../../action/SearchActions');
var SearchUitl = require('../../../../util/SearchUtil');
var SelectedItem = require('./SelectedItem.react');

const SelectedFilterDates = React.createClass({

    render(){
        var data = this.props.data;
        var select = Functions.dateSelect();
        var filters = data.filterDates;
        if(select.length == 0) return null;
        if(filters.length == 0) return null;

        return(
            <div>
                {filters.map(function(result, index){
                    return  <SelectedItem key={index} data={result} select={select} type="date"/>
                }.bind(this))}
            </div>
        )
    }

});


module.exports = SelectedFilterDates;