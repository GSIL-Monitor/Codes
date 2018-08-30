/**
 * Created by haiming on 16/2/3.
 */
var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ValidateStore = require('../../../../../store/validation/NewCompanyStore');
var ValidateActions = require('../../../../../action/validation/NewCompanyActions');
var Functions = require('../../../../../../../react-kit/util/Functions');
var FormInput = require('../FormInput.react');

const Brief = React.createClass({

    mixins: [Reflux.connect(ValidateStore, 'validate')],

    render(){
        var hint;
        var className='form-input-full'
        if(!Functions.isEmptyObject(this.state)) {
            var validate = this.state.validate.brief;
            if (!Functions.isEmptyObject(validate)) {
                    if (!validate.validation) {
                        className += ' error';
                        hint = <span className="text-red">{validate.hint}</span>;
                    }
            }
        }

        return <FormInput label='一句话简介'
                          name='brief'
                          required={true}
                          value={this.props.data}
                          className={className}
                          onChange={this.change}
                          onBlur={this.blur}
                          hint= {hint}
                          id={this.props.id}
            />
    },

    change(e){
        ValidateActions.change(e.target.name);
        this.props.onChange(e);
    },

    blur(e){
        ValidateActions.brief(e.target.value);
    }

});


module.exports = Brief;
