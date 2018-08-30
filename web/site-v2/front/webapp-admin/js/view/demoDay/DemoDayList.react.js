var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var SiteDemoDayList = require('../../../../webapp-site/js/view/demoDay/DemoDayList.react');

const DemoDayList = React.createClass({

    render(){
        return (
            <div>
                <div><button className="btn btn-navy" onClick={this.create}>新建</button></div>
                <SiteDemoDayList from="admin"/>
            </div>
        )
    },

    create(){
        window.location.href="/admin/#/new/demoday";
    }

});

module.exports = DemoDayList;

