var React = require('react');
var CollectionActions = require('../../../action/collection/CollectionActions');
var NewCollectionActions = require('../../../action/collection/NewCollectionActions');
var CollectionUtil = require('../../../util/CollectionUtil');

const FilterItem = React.createClass({
    render(){
        var data = this.props.data;
        var selected = this.props.selected;
        var type = this.props.type;
        var from = this.props.from;

        var className = 'filter-item ';
        if(CollectionUtil.isSelected(data, selected))
            className += 'filter-item-selected';

        return (
            <span className={className} onClick={this.click}>
                {data.name}
            </span>
        )
    },

    click(){
        var from = this.props.from;
        var data = this.props.data;
        var type = this.props.type;
        if(from == 'collection')
            CollectionActions.filter(data, type);
        else
            NewCollectionActions.select(data, type);
    }
});

module.exports = FilterItem;