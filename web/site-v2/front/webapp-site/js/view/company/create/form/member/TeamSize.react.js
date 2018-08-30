var React = require('react');
var ReactPropTypes = React.PropTypes;
var Reflux = require('reflux');

var ValidateStore = require('../../../../../store/validation/NewCompanyStore');
var ValidateActions = require('../../../../../action/validation/NewCompanyActions');
var Functions = require('../../../../../../../react-kit/util/Functions');
var FormSelect = require('../FormSelect.react');
var CreateCompanyUtil = require('../../../../../util/CreateCompanyUtil');

const TeamSize = React.createClass({
        render(){
            var teamSize=CreateCompanyUtil.teamSize;

            return(

                <div className="create-company-form">

                    <div className='cc-form-left'>
                        <span>团队规模</span>
                    </div>
                    <div className="cc-form-right">
                        <div className="form-input">
                            <FormSelect  className='cc-form-select'
                                        name='teamSize'
                                        value={this.props.data}
                                        select={teamSize}
                                />
                        </div>

                    </div>
                </div>
            )
        }

    }
);
module.exports=TeamSize