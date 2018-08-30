var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ProductStore = require('../../../store/company/ProductStore');
var ProductActions = require('../../../action/company/ProductActions');
var CompanyUtil = require('../../../util/CompanyUtil');
var ProductUtil = require('../../../util/ProductUtil');
var Functions = require('../../../../../react-kit/util/Functions');
var DivExtend = require('../../../../../react-kit/basic/DivExtend.react');


var ProductNav = require('./ProductNav.react');
var ProductList = require('./ProductList.react');

const Product = React.createClass({

    mixins: [Reflux.connect(ProductStore, 'data')],

    componentWillMount() {
        ProductActions.get(this.props.id);
    },

    componentWillReceiveProps(nextProps) {
        if (this.props.id == nextProps.id) return;
        ProductActions.get(nextProps.id);
    },

    render(){
        var state = this.state;
        if (Functions.isEmptyObject(state))
            return null;

        var data = state.data;
        var list = data.list;
        if (list.length == 0) return null;

        var count = state.data.count;
        if (count > 100) {
            count = 99;
        }

        var showAll = this.state.data.showAll;
        var more;
        var len = 6;
        if (list.length > len) {
            list = CompanyUtil.getSubList(list, len, showAll);
            if (showAll) {
                more = <DivExtend type="less" extend={this.extend}/>
            }
            else {
                more = <DivExtend type="more" extend={this.extend}/>
            }
        }

        return (
            <div className="section">
                <span className="section-header">
                    产品介绍
                </span>

                <section className="section-body">
                    <ProductNav data={data} />

                    <ProductList data={list}/>

                    {more}

                </section>
            </div>

        )
    },

    extend(){
        ProductActions.showAll();
    }

});






module.exports = Product;