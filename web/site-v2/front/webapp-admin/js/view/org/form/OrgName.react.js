var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ValidateStore = require('../../../store/validation/ValidateOrgStore');
var ValidateActions = require('../../../action/validation/ValidateOrgActions');
var Functions = require('../../../../../react-kit/util/Functions');
var FormInput = require('../../../../../webapp-site/js/view/company/create/form/FormInput.react');

const OrgName = React.createClass({

    mixins: [Reflux.connect(ValidateStore, 'validate')],

    render(){
        var hint;
        var className='form-input-full';
        if(!Functions.isEmptyObject(this.state)){
            var validate = this.state.validate.name;
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

        return <FormInput label='机构名称'
                          name='name'
                          value={this.props.data}
                          className={className}
                          onChange={this.change}
                          onBlur={this.blur}
                          hint= {hint}
                          required={true}
                          admin={true}
                          id={this.props.id}
            />
    },

    change(e){
        ValidateActions.change(e.target.name);
        this.props.onChange(e);
    },

    blur(e){
            ValidateActions.name(e.target.value);
    }

});


module.exports = OrgName;