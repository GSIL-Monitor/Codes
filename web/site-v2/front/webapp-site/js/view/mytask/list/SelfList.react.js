var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var MytaskActions = require('../../../action/MytaskActions');
var Functions = require('../../../../../react-kit/util/Functions');
var DivFindNone = require('../../../../../react-kit/basic/DivFindNone.react.js');
var CompanyItem = require('./CompanyItem.react');

const SelfList = React.createClass({
    render(){
        if(Functions.isEmptyObject(this.props))
            return null;

        var list = this.props.list;
        var count = this.props.count;
        if(list.length == 0){
            return <DivFindNone />
        }

        return (
            <div>
                {list.map(function (result, index) {
                    return <CompanyItem key={index} data={result} from="self"/>;
                }.bind(this))}
            </div>
        )
    }

    //clickMore() {
    //    MytaskActions.listMore(23010);
    //}
});


module.exports = SelfList;