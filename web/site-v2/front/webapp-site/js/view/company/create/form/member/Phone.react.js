var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ValidateStore = require('../../../../../store/validation/NewCompanyStore');
var ValidateActions = require('../../../../../action/validation/NewCompanyActions');
var Functions = require('../../../../../../../react-kit/util/Functions');
var FormInput = require('../FormInput.react');

const Phone = React.createClass({

    mixins: [Reflux.connect(ValidateStore, 'validate')],

    componentWillMount: function () {
        ValidateActions.getInitData();
    },
    render(){
        var hint;
        var className = 'form-input-short';
        if (!Functions.isEmptyObject(this.state)) {
            var validate = this.state.validate.phone;
            if (!Functions.isEmptyObject(validate)) {
                if (!validate.validation) {
                    className += ' error';
                    hint = <span className="text-red">{validate.hint}</span>;
                }
            }
        }

        return <FormInput label='联系方式'
                          name='phone'
                          value={this.props.data}
                          className={className}
                          onChange={this.change}
                          onBlur={this.blur}
                          hint={hint}
            />
    },

    change(e){
        ValidateActions.change(e.target.name);
        this.props.onChange(e);
    },

    blur(e){
        if (e.target.value != null && e.target.value.trim() != '') {
            ValidateActions.phone(e.target.name, e.target.value);
        }

    }

});


module.exports = Phone;