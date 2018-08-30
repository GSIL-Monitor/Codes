var React = require('react');
var CollectionUtil = require('../../../util/CollectionUtil');
var CollectionForm = require('./CollectionForm.react.js');

const InvestorFilters = React.createClass({

    render(){
        var data = this.props.data;
        var selected = data.selectedInvestors;

        var list = CollectionUtil.investorSelect;

        return(
            <CollectionForm label='过往投资机构' list={list} type='investor' selected={selected}/>
        )
    }

});

module.exports = InvestorFilters;