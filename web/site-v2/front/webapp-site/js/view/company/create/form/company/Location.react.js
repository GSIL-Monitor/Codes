var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ValidateStore = require('../../../../../store/validation/NewCompanyStore');
var ValidateActions = require('../../../../../action/validation/NewCompanyActions');
var Functions = require('../../../../../../../react-kit/util/Functions');
var FormLocationInput = require('../FormLocationInput');

const Location = React.createClass({

    mixins: [Reflux.connect(ValidateStore, 'validate')],

    render(){
        var hint;
        var className = 'cc-form-location';
        if(!Functions.isEmptyObject(this.state)){
            var validate = this.state.validate.locationId;
            if(!Functions.isEmptyObject(validate)){
                if(!validate.validation){
                    className += ' error';
                    hint = <span className="text-red">{validate.hint}</span>;
                }
            }

        }
        return <FormLocationInput label='公司地点'
                          name='locationId'
                          required={true}
                          value={this.props.data}
                          className= {className}
                          from = 'createCompany'
                          hint= {hint}
                          id={this.props.id}
            />
    }

});


module.exports = Location;