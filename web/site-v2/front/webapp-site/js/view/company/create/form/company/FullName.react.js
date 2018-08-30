var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ValidateStore = require('../../../../../store/validation/NewCompanyStore');
var ValidateActions = require('../../../../../action/validation/NewCompanyActions');
var Functions = require('../../../../../../../react-kit/util/Functions');
var FormInput = require('../FormInput.react');

const Name = React.createClass({

    mixins: [Reflux.connect(ValidateStore, 'validate')],

    render(){
        var hint;
        var className='form-input-full';
        if(!Functions.isEmptyObject(this.state)){
            var validate = this.state.validate.fullName;
            if(!Functions.isEmptyObject(validate)){
                if(validate.show)
                    hint = <span className="text-red">{validate.hint}</span>;
                if(!validate.validation){
                    className += ' error';
                }
                else if(validate.show&&validate.hint=='usable'){
                    hint = <span className="cc-text-green"><i className="fa fa-check"></i></span>;
                }
            }

        }

        return <FormInput label='公司全称'
                          name='fullName'
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
        if(e.target.value.trim()!='') {
            ValidateActions.fullName(e.target.value);
        }
    }

});


module.exports = Name;