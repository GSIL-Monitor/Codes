var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var MytaskActions = require('../../../action/MytaskActions');
var Functions = require('../../../../../react-kit/util/Functions');
var DivFindNone = require('../../../../../react-kit/basic/DivFindNone.react.js');
var ColdcallItem = require('./ColdcallItem.react');

const PublishList = React.createClass({
    render(){
        if(Functions.isEmptyObject(this.props))
            return null;

        var list= this.props.list;
        var count = this.props.count;

        if(list.length == 0){
            return <DivFindNone />
        }

        return (
            <div>
                {list.map(function (result, index) {
                    return <ColdcallItem key={index} data={result}/>;
                }.bind(this))}
            </div>
        )
    },

    clickMore() {
        MytaskActions.listMore(2);
    }
});


module.exports = PublishList;


