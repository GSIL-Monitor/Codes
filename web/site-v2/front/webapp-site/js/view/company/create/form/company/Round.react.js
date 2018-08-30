var React = require('react');
var ReactPropTypes = React.PropTypes;
var Reflux = require('reflux');
var $ = require('jquery');

var InputText = require('../../../../../../../react-kit/form/InputText.react');
var ValidateStore = require('../../../../../store/validation/NewCompanyStore');
var ValidateActions = require('../../../../../action/validation/NewCompanyActions');
var Functions = require('../../../../../../../react-kit/util/Functions');
var FormSelect = require('../FormSelect.react');
var CreateCompanyUtil = require('../../../../../util/CreateCompanyUtil');

const Round = React.createClass({
        mixins: [Reflux.connect(ValidateStore, 'validate')],
        render(){
            var rounds=CreateCompanyUtil.round;
            var className = 'cc-form-select';
            if(!Functions.isEmptyObject(this.state)) {
                var validate = this.state.validate.round;
                if (!Functions.isEmptyObject(validate)) {
                    if (!validate.validation) {
                        className += ' error';
                    }
                }
            }

           return(

               <div className="create-company-form" id={this.props.id} tabIndex="-1" style={{outline:"none"}} >

                   <div className='cc-form-left'>
                       <span className='left-required'>*</span>
                       <span>融资阶段</span>
                   </div>
                   <div className="cc-form-right">
                       <div className="form-input">
                           <FormSelect  className={className}
                                       name='round'
                                       value={this.props.data}
                                       select={rounds}
                               />
                       </div>
                   </div>
               </div>
           )
        }

    }
);
module.exports=Round