var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanyStore = require('../../../store/CompanyStore');
var CompanyActions = require('../../../action/CompanyActions');
var CompanyUtil = require('../../../util/CompanyUtil');
var Functions = require('../../../../../react-kit/util/Functions');
var DivExtend = require('../../../../../react-kit/basic/DivExtend.react');


const Footprints = React.createClass({
    render(){
        var data = this.props.data;
        var list = data.footprints;
        if(list == null) return null;
        if(list.length ==0) return null;

        var showAll = data.footprintAll;

        var more;
        var len = 5;
        if(list.length > len){
            list = CompanyUtil.getSubList(list, len, showAll);
            if(showAll){
                more = <DivExtend type="less" extend={this.extend}/>
            }
            else{
                more = <DivExtend type="more" extend={this.extend}/>
            }
        }

        var className = 'section-body ';

        if(data.fundings.length > 2 && data.fundings.length < 7){
            className += ' m-t--10'
        }

        return(
            <section className={className}>
                <div className="section-round">
                    <div className="section-name name3">
                        里程碑
                    </div>
                </div>
                <div className="section-content footprint-section">
                    {list.map(function (result, index) {
                        return <FootprintItem key={index} data={result}/>;
                    })}

                    {more}

                </div>
            </section>
        )
    },

    extend(){
        CompanyActions.showFootprintAll();
    }

});

const FootprintItem = React.createClass({
    render(){
        var data = this.props.data;

        return(
            <div className="section-sub-item">
                <div className="section-sub-item-name">{data.footDate.substring(0,7)}</div>
                <div className="section-sub-item-content">{data.description}</div>
            </div>
        )
    }
});

module.exports = Footprints;