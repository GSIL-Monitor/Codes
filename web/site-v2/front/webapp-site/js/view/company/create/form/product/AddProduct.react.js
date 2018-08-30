var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');
var NewProduct = require('./NewProduct.react');
var ValidateStore = require('../../../../../store/validation/NewCompanyStore');
var ValidateActions = require('../../../../../action/validation/NewCompanyActions');
var Functions = require('../../../../../../../react-kit/util/Functions');
const AddProduct = React.createClass({
    mixins: [Reflux.connect(ValidateStore, 'validate')],
    render(){
        var hint;
        if (!Functions.isEmptyObject(this.state)) {
            var validate = this.state.validate.product;
            if (!Functions.isEmptyObject(validate)) {
                if (!validate.validation) {
                    hint = <span className="text-red">{validate.hint}</span>;
                }
            }
        }

        var data = this.props.data;
        return (
            <div className="create-company-form" id={this.props.id} tabIndex="-1" style={{outline:"none"}}>

                <div className='cc-form-left '>
                    <span className='left-required'>*</span>
                    <span>产品类型</span>
                </div>

                <div className="cc-form-right cc-position-product">
                    <h3 className="m-t--2">请选择产品具体形态，并填写链接</h3>
                    <NewProduct data={data}/>
                </div>
                <div className="form-hint product-hint">
                    {hint}
                </div>
            </div>
        )

    }
});
module.exports = AddProduct;


