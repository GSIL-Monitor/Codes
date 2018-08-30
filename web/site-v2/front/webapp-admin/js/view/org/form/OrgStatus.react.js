var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ValidateStore = require('../../../store/validation/ValidateOrgStore');
var ValidateActions = require('../../../action/validation/ValidateOrgActions');
var Functions = require('../../../../../react-kit/util/Functions');
var FormInput = require('../../../../../webapp-site/js/view/company/create/form/FormInput.react');

const OrgStatus = React.createClass({


    render(){
        return (
            <div className="create-company-form" id={this.props.id} tabIndex="-1" style={{outline:"none"}} >

            <div className='cc-form-left cc-org-left'>
                <span className='left-required'>*</span>
                <span>机构状态</span>
            </div>
            <div className="cc-form-right">
                <div className="form-input">
                   X
                </div>
            </div>
        </div>)
    },

    change(e){
        ValidateActions.change(e.target.name);
        this.props.onChange(e);
    },

    blur(e){
        ValidateActions.name(e.target.value);
    }

});


module.exports = OrgStatus;