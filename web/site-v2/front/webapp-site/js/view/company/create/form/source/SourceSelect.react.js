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

var SourceSelect = React.createClass({

    mixins: [Reflux.connect(ValidateStore, 'validate')],

    render: function() {
        var sources = CreateCompanyUtil.sources;

        return (
            <div className="create-company-form" id={this.props.id} tabIndex="-1" style={{outline:"none"}}>
                <div className='cc-form-left'>
                    <span>产品来源</span>
                </div>
                <div className="cc-form-right">
                    <div className="form-input">
                        <FormSelect name='source'
                                    className="cc-form-select"
                                    value={this.props.data}
                                    select={sources}
                            />
                    </div>
                </div>
            </div>
        );
    },
});

module.exports = SourceSelect;
