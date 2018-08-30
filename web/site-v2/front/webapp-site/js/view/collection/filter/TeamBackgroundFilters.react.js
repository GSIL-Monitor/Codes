var React = require('react');
var CollectionUtil = require('../../../util/CollectionUtil');
var CollectionForm = require('./CollectionForm.react.js');

const TeamBackgroundFilters = React.createClass({

    render(){
        var data = this.props.data;
        var selected = data.selectedBackgrounds;

        var list = CollectionUtil.teamBackgroundSelect;

        return(
            <CollectionForm label='团队背景' list={list} type='background' selected={selected}/>
        )
    }

});

module.exports = TeamBackgroundFilters;