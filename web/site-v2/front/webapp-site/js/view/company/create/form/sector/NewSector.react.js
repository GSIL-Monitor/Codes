var React = require('react');
var ReactPropTypes = React.PropTypes;
var Reflux = require('reflux');
var $ = require('jquery');

var InputText = require('../../../../../../../react-kit/form/InputText.react');
var ValidateStore = require('../../../../../store/validation/NewCompanyStore');
var ValidateActions = require('../../../../../action/validation/NewCompanyActions');
var Functions = require('../../../../../../../react-kit/util/Functions');
var FormSelect = require('../FormSelect.react');

var NewSector = React.createClass({

    mixins: [Reflux.connect(ValidateStore, 'validate')],

    render: function() {
        var  className='cc-form-select';
        if(!Functions.isEmptyObject(this.state)) {
            var validate = this.state.validate.sector;
            if (!Functions.isEmptyObject(validate)) {
                if (!validate.validation) {
                    className += ' error';
                }
            }
        }

        var parentSectors = this.props.parentSectors;
        var subSectors = this.props.subSectors;
        var parentSectorId = this.props.parentSectorId;
        var subSectorId = this.props.subSectorId;

        var sectors=[{name:'请选择',value:-1}];
        for(var i in parentSectors){
            var sector = {};
            sector.name = parentSectors[i].sectorName;
            sector.value = parentSectors[i].id;
            sectors.push(sector)
        }

        var subs = [];
        for(var i in subSectors){
            var sub = {};
            sub.name = subSectors[i].sectorName;
            sub.value = subSectors[i].id;
            subs.push(sub)
        }

        return (
            <div className="create-company-form" id={this.props.id} tabIndex="-1" style={{outline:"none"}}>
                <div className='cc-form-left'>
                    <span className='left-required'>*</span>
                    <span>行业</span>
                </div>
                <div className="cc-form-right">
                    <div className="form-input">
                        <FormSelect id={this.props.id}
                                name='parentSector'
                                className={className}
                                value={parentSectorId}
                                select={sectors}
                            />
                        <FormSelect className='second-sector'
                                name='subSector'
                                className='cc-form-select'
                                value={subSectorId}
                                select={subs}
                            />
                    </div>
                </div>
            </div>
        );
    },
});

module.exports = NewSector;
