var React = require('react');
var SearchActions = require('../../../../action/SearchActions');
var SearchUitl = require('../../../../util/SearchUtil');

const SelectedItem = React.createClass({

    render(){
        var selectClass = "select-span sector-span filter-selected";
        var type = this.props.type;
        var name;

        if(type == 'sector'){
            name = SearchUitl.getSectorName(this.props.data, this.props.select);
        }else if(type =='date'){
            name = SearchUitl.getDateName(this.props.data, this.props.select);
        }else{
            name = SearchUitl.getSelectedName(this.props.data, this.props.select);
        }

        return  <span className={selectClass} >
                     {name}
                    <i className="fa fa-times m-l-5" onClick={this.handleClick}></i>
                </span>
    },

    handleClick(){
        SearchActions.removeFilterItem(this.props.type, this.props.data);
    }
});

module.exports = SelectedItem;