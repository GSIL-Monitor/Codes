var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CollectionHead = require('./CollectionHead.react.js');
var CompanyItem =  require('./CompanyItem.react');
var NewProductItem = require('./NewProductItem.react');
var Loading = require('../../../../react-kit/basic/Loading.react');
var DivFindNone = require('../../../../react-kit/basic/DivFindNone.react');

const CollectionTimeline = React.createClass({

    render(){
        var data= this.props.data;
        var list = data.timeline;
        if(list == null){
            return (   <div>
                    <div className="selected-collection-name">发现动态</div>
                    <Loading/>
                </div>
            )
        }

        if(list.length == 0) {
            return (
                <div>
                    <div className="selected-collection-name">发现动态</div>
                    <DivFindNone/>
                </div>
            )
        }
        return (
            <div>
                <CollectionHead name="发现动态" data={data}/>

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
        if(data.type == 14020)
            return <NewProductItem data={data} />
        else
            return <CompanyItem data={data}/>
    }

});






module.exports = CollectionTimeline;

