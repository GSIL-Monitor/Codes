var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ValidateStore = require('../../../store/validation/ValidateDemodayStore');
var ValidateActions = require('../../../action/validation/ValidateDemodayActions');
var Functions = require('../../../../../react-kit/util/Functions');
var FormInput = require('../../../../../webapp-site/js/view/company/create/form/FormInput.react.js');

const HoldEndDate = React.createClass({

    mixins: [Reflux.connect(ValidateStore, 'validate')],

    render(){
        var hint;
        var className='form-input-short';
        if (!Functions.isEmptyObject(this.state)) {
            var validate = this.state.validate.holdEndDate;
            if (!Functions.isEmptyObject(validate)) {
                if (!validate.validation) {
                    className += ' error';
                    hint = <span className="text-red">{validate.hint}</span>;
                }
            }
        }

        return <FormInput label='结束日期'
                          name='holdEndDate'
                          className={className}
                          value={this.props.data}
                          onChange={this.change}
                          onBlur={this.blur}
                          hint={hint}
                          admin={true}
                          required={true}
                          id={this.props.id}
                          placeholder="2016-01-01 00:00"
            />
    },

    change(e){
        ValidateActions.change(e.target.name);
        this.props.onChange(e);
    },

    blur(e){
        ValidateActions.date(e.target.name,e.target.value);
        //this.props.onBlur(e.target.value);
    }

});


module.exports = HoldEndDate;