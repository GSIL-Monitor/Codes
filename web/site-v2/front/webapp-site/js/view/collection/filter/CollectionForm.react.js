var React = require('react');
var FilterItem = require('./FilterItem.react.js');

var TagInput = require('../../../../../react-kit/basic/search/TagInput.react');
var LocationInput = require('../../../../../react-kit/basic/search/LocationInput.react');

const CollectionForm = React.createClass({
    render(){
        var list = this.props.list;
        var selected = this.props.selected;
        var type = this.props.type;
        var from = this.props.from;

        return (
            <div className="collection-form">

                <div className="collection-form-left">
                    <span>{this.props.label}</span>
                </div>

                <div className="collection-form-right">
                    {list.map(function(result, index){
                        return <FilterItem data={result}
                                           selected={selected}
                                           type={type}
                                           from={from}
                                           key={index} />
                    })}

                    <Search type={type} from={from}/>

                </div>
            </div>
        )
    }
});

const Search = React.createClass({
    render(){
        var type = this.props.type;
        var from = this.props.from;

        if(type == 'tag')
            return (
                <div className="left">
                    <span className="collection-filter-more">更多标签：</span>
                    <TagInput from="newCollection"/>
                </div>
                );
        else if(type == 'location')
            return (
                <div className="left">
                    <span className="collection-filter-more">更多地区：</span>
                    <LocationInput from="newCollection"/>
                </div>
            );
        else
            return null;
    }
});

module.exports = CollectionForm;