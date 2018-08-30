var React = require('react');
var CollectionForm = require('./CollectionForm.react.js');

const TagFilters = React.createClass({

    render(){
        var data = this.props.data;
        var list = data.tags;
        var selected = data.selectedTags;

        var from = this.props.from;
        return(
            <CollectionForm label='热门标签' list={list} type='tag' selected={selected} from={from}/>
        )
    }

});

module.exports = TagFilters;