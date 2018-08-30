var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompsStore = require('../../../../../webapp-site/js/store/company/CompsStore');
var CompsActions = require('../../../../../webapp-site/js/action/company/CompsActions');
var CompanyUtil = require('../../../../../webapp-site/js/util/CompanyUtil');
var Functions = require('../../../../../react-kit/util/Functions');
var CompanyList = require('../../../../../react-kit/company/CompanyList.react');

const Comps = React.createClass({

    mixins: [Reflux.connect(CompsStore, 'data')],

    componentWillMount() {
        CompsActions.get(this.props.id);
    },

    componentWillReceiveProps(nextProps) {
        if(this.props.id == nextProps.id) return;
        CompsActions.get(nextProps.id);
    },

    render(){
        if (Functions.isEmptyObject(this.state))
            return null;

        var data = this.state.data.list;
        if(data.length ==0) return null;

        var showAll = this.state.data.showAll;
        return (
            <div className="section">
                <span className="section-header">
                    竞争对手
                </span>

                <section className="section-body">
                    <CompanyList data={data} more={showAll} extend={this.extend}/>
                </section>
            </div>

        )
    },

    extend(){
        CompsActions.showAll();
    }
});

module.exports = Comps;