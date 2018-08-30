var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanyUtil = require('../../webapp-site/js/util/CompanyUtil');
var Functions = require('../../react-kit/util/Functions');


const Footprints = React.createClass({
    render(){
        var data = this.props.data;
        if(data.length ==0) return null;

        var len = 3;
        if(data.length > len){
            data = CompanyUtil.getSubList(data, len, false);
        }

        return(
            <section>
                <span className="pop-section-name">里程碑</span>
                <div className="m-t-5">
                    {data.map(function (result, index) {
                        return <FootprintItem key={index} data={result}/>;
                    })}
                </div>
            </section>
        )
    }

});

const FootprintItem = React.createClass({
    render(){
        var data = this.props.data;

        return(
            <div className="pop-footprint-item m-b-5">
                <div className="pop-footprint-date">{data.footDate.substring(0,7)}</div>
                <div className="pop-footprint-content">{data.description}</div>
            </div>
        )
    }
});

module.exports = Footprints;