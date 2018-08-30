var React = require('react');
var $ = require('jquery');

var Functions = require('../../../../../react-kit/util/Functions');
var DivFindNone = require('../../../../../react-kit/basic/DivFindNone.react.js');
var ColdcallItem = require('./ColdcallItem.react');
var CompanyItem = require('./CompanyItem.react');

const TaskList = React.createClass({
    render(){
        if(Functions.isEmptyObject(this.props))
            return null;

        var list = this.props.list;
        var count = this.props.count;
        if(list == null) return <DivFindNone />;
        if(list.length == 0) return <DivFindNone />;

        return (
            <div>
                { list.map(function (result, index) {
                    return <ListItem key={index} data={result}/>;
                }.bind(this))}
            </div>
        )
    },

    clickMore() {
        this.props.listMore();
    }
});



const ListItem = React.createClass({
    render(){
        var data = this.props.data;

        var coldcallId = data.coldcallId;
        var detail;
        if(coldcallId == null){
            detail = <CompanyItem data={data} from="recommend"/>
        }else{
            detail = <ColdcallItem data={data}/>
        }

        return(
               <div>{detail}</div>
        )
    }
});




module.exports = TaskList;