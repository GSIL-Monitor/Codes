var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ValidateStore = require('../../../../../store/validation/NewCompanyStore');
var ValidateActions = require('../../../../../action/validation/NewCompanyActions');
var Functions = require('../../../../../../../react-kit/util/Functions');
var FormInput = require('../FormInput.react');
var FormSelect = require('../FormSelect.react');
var CreateCompanyUtil = require('../../../../../util/CreateCompanyUtil');

const Investment = React.createClass({
    mixins: [Reflux.connect(ValidateStore, 'validate')],

    componentWillMount: function () {
        ValidateActions.getInitData();
    },
    render(){
        var currency = CreateCompanyUtil.currency;
        var hint;
        var className = 'form-input-short';
        if (!Functions.isEmptyObject(this.state)) {
            var validate = this.state.validate.investment;
            if (!Functions.isEmptyObject(validate)) {
                if (!validate.validation) {
                    className += ' error';
                    hint = <span className="text-red">{validate.hint}</span>;
                }
            }
        }
        return (

            <div className="create-company-form">

                <div className='cc-form-left'>
                    <span>融资金额</span>
                </div>

                <div className="cc-form-right">
                    <div className="form-input">
                        <input type="text"
                               className={className}
                               name='investment'
                               value={this.props.data}
                               placeholder={this.props.placeholder}
                               onChange={this.change}
                               onBlur={this.blur}
                            />
                        <FormSelect className='cc-currency'
                                    name='currency'
                                    value={this.props.currency}
                                    select={currency}
                            />
                    </div>
                    <div className="form-hint">
                        {hint}
                    </div>
                </div>
            </div>
        );
    },

    change(e){
        ValidateActions.investment(e.target.name, e.target.value);
        this.props.onChange(e)
    },
    blur(e){
        var validate = this.state.validate.investment;
        if (e.target.value.trim()!=''&&!validate.validation) {
            e.target.focus();
        }
    }

});


module.exports = Investment;