var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CollectionActions = require('../../action/collection/CollectionActions');
var CompanyItem = require('./CompanyItem.react');
var NewProductItem = require('./NewProductItem.react');
var Loading = require('../../../../react-kit/basic/Loading.react');
var DivFindNone = require('../../../../react-kit/basic/DivFindNone.react');

const CollectionCompanies = React.createClass({

    render(){
        var list = this.props.list;
        if (list == null) {
            return <Loading/>;
        }
        var collectionName = this.props.collection.name;
        if (list.length == 0) {
            return ( <div>
                    <div className="selected-collection-name">{collectionName}</div>
                    <DivFindNone/>
                </div>
            )
        }
        return (
            <div>
                <div className="selected-collection-name">{collectionName}</div>
                <div className="collection-timeline">
                    { list.map(function (result, index) {
                        return <TimelineItem key={index} data={result}/>;
                    }.bind(this))}
                </div>
            </div>
        )
    }

});


const TimelineItem = React.createClass({

    render(){
        var data = this.props.data;
        if (data.type == 14020)
            return <NewProductItem data={data}/>;
        else
            return <CompanyItem data={data}/>;
    }

});


module.exports = CollectionCompanies;

