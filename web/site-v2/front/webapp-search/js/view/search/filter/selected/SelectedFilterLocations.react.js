var React = require('react');
var Functions = require('../../../../../../react-kit/util/Functions');
var SearchActions = require('../../../../action/SearchActions');
var SearchUitl = require('../../../../util/SearchUtil');
var SelectedItem = require('./SelectedItem.react');

const SelectedFilterLocations = React.createClass({

    render(){
        var data = this.props.data;
        var select = Functions.locationUseful();
        var filters = data.filterLocations;
        if(select.length == 0) return null;
        if(filters.length == 0) return null;

        return(
            <div>
                {filters.map(function(result, index){
                    return  <SelectedItem key={index} data={result} select={select} type="location"/>
                }.bind(this))}
            </div>
        )
    }

});


module.exports = SelectedFilterLocations;