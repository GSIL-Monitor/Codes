var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompsStore = require('../../../store/company/CompsStore');
var CompsActions = require('../../../action/company/CompsActions');
var CompanyUtil = require('../../../util/CompanyUtil');
var Functions = require('../../../../../react-kit/util/Functions');
var CompanyList = require('../../../../../react-kit/company/CompanyList.react');


const Comps = React.createClass({

    render(){
        if (Functions.isEmptyObject(this.props.data))
            return null;

        var data = this.props.data.list;
        if(data.length ==0) return null;

        var showAll = this.props.data.showAll;

        var update;

        return (
            <div className="section">
                <span className="section-header">
                    竞争对手
                </span>

                <a className="update-company" onClick={this.update}>
                    修改
                </a>

                <section className="section-body">

                    <CompanyList data={data} more={showAll} extend={this.extend}/>

                </section>
            </div>

        )
    },

    extend(){
        CompsActions.showAll();
    },

    update(){
        CompsActions.update();
    }

});



module.exports = Comps;