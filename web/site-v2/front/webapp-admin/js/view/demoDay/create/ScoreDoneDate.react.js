var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ValidateStore = require('../../../store/validation/ValidateDemodayStore');
var ValidateActions = require('../../../action/validation/ValidateDemodayActions');
var Functions = require('../../../../../react-kit/util/Functions');
var FormInput = require('../../../../../webapp-site/js/view/company/create/form/FormInput.react.js');

const ScoreDoneDate = React.createClass({

    mixins: [Reflux.connect(ValidateStore, 'validate')],

    render(){
        var hint;
        var className='form-input-short';
        if (!Functions.isEmptyObject(this.state)) {
            var validate = this.state.validate.scoreDoneDate;
            if (!Functions.isEmptyObject(validate)) {
                if (!validate.validation) {
                    className += ' error';
                    hint = <span className="text-red">{validate.hint}</span>;
                }
            }
        }

        return <FormInput label='筛选结束日期'
                          name='scoreDoneDate'
                          className={className}
                          value={this.props.data}
                          onChange={this.change}
                          onBlur={this.blur}
                          hint={hint}
                          admin={true}
            />
    },

    change(e){
        ValidateActions.change('scoreDoneDate');
        this.props.onChange(e);
    },

    blur(e){
        if(this.props.update&&e.target.value===this.props.oldData)return;
        ValidateActions.date(e.target.value,'scoreDoneDate');
    }

});


module.exports = ScoreDoneDate;