var React = require('react');
var CollectionUtil = require('../../../util/CollectionUtil');
var CollectionForm = require('./CollectionForm.react.js');

const EstablishDateFilters = React.createClass({

    render(){
        var data = this.props.data;
        var selected = data.selectedDates;

        var list = CollectionUtil.dateSelect();

        return(
            <CollectionForm label='创立时间' list={list} type='date' selected={selected}/>
        )
    }

});

module.exports = EstablishDateFilters;