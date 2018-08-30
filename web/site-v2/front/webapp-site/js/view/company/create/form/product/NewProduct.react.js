var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');
var Functions = require('../../../../../../../react-kit/util/Functions');
var ButtonAdd = require('../../../../../../../react-kit/basic/ButtonAdd.react');
var FormSelect = require('../FormSelect.react');

var CreateCompanyActions = require('../../../../../action/CreateCompanyActions');
var CreateCompanyStore = require('../../../../../store/CreateCompanyStore');
var ValidateActions = require('../../../../../action/validation/NewCompanyActions');


const NewProduct = React.createClass({


    render(){
        var products = [4010, 4020, 4030, 4040, 4050, 4099];
        return (
            <div>
                {products.map(function (result, index) {
                    return <ProductItem key={index} data={result}/>
                })}
            </div>
        )
    }

});


const ProductItem = React.createClass({

    mixins: [Reflux.connect(CreateCompanyStore, 'data')],

    render(){
        var type = this.props.data;
        var name = Functions.getArtifactTypeName(type);
        var list = [];
        if (!Functions.isEmptyObject(this.state)) {
            list = this.state.data.productList;
        }

        var flag;
        var productName='';
        if (list.length > 0) {
            for (var i in list) {
                if (this.props.data == list[i].type) {
                    if (list[i].selected)
                        flag = true;
                    productName = list[i].name;
                }
            }
        }

        var className = 'product-select ';
        if (flag) className += 'product-selected';

        var placeholder= "名称/链接";
        if(type == 4010){
            placeholder = '链接';
        }else if(type == 4099){
            placeholder = '填写产品的描述（例:线下实体）';
        }

        return (
            <div className="new-product-item">
                <div className="product-item-info">
                    <div className={className} onClick={this.click} ref='selected'></div>
                    <span>{name}</span>
                    <input type="text"
                           placeholder = {placeholder}
                           className="product-input"
                           value={productName}
                           onChange={this.handleChange}
                           onBlur={this.blur} />
                </div>
                <div className="product-item-hint">

                </div>
            </div>
        )
    },

    click(){
        CreateCompanyActions.selectProduct(this.props.data);
        ValidateActions.product(this.state.data.productList);
    },

    handleChange(event){
        CreateCompanyActions.addProductName(this.props.data, event.target.value);
        ValidateActions.product(this.state.data.productList);
    },

    blur(e){
        if(this.props.data == 4010){
            ValidateActions.productWebsite(e.target.value);
        }
    }
});

module.exports = NewProduct;