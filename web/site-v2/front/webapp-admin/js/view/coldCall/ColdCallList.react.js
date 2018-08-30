var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ColdCallActions = require('../../action/ColdCallActions');

var Functions = require('../../../../react-kit/util/Functions');
var ButtonLoadMore = require('../../../../react-kit/basic/ButtonLoadMore.react');
var DivFindNone = require('../../../../react-kit/basic/DivFindNone.react');
var  ListElement = require('../../../../webapp-site/js/view/mytask/list/ColdcallItem.react');

const ColdCallList = React.createClass({

    render(){
        if(Functions.isEmptyObject(this.props))
            return null;

        var list ;

        var coldCall_Type =this.props.data.coldCall_Type;

        var more = "";
        if(coldCall_Type==0){
            list  = this.props.data.unmatched_list;
            if(list.length == 0){
                return <DivFindNone />
            }

        }
        else if(coldCall_Type==1){
            list=this.props.data.matched_list;
            if(list.length == 0){
                return <DivFindNone />
            }
        }
        return (
            <div>
                { list.map(function (result, index) {
                    return <ListElement key={index} data={result}  admin={true}/>;
                }.bind(this))}
                {more}
            </div>
        )
    },
    clickMore() {
        ColdCallActions.listMore(this.props.data.coldCall_Type);
    }
});


module.exports = ColdCallList;