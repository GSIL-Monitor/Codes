var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ValidateStore = require('../../../../../store/validation/NewCompanyStore');
var ValidateActions = require('../../../../../action/validation/NewCompanyActions');
var Functions = require('../../../../../../../react-kit/util/Functions');
var FormInput = require('../FormInput.react');

const ShareRatio = React.createClass({

    mixins: [Reflux.connect(ValidateStore, 'validate')],
    componentWillMount: function () {
        ValidateActions.getInitData();
    },

    render(){
        var hint;
        var className = 'cc-sharesRatio-input';
        if(!Functions.isEmptyObject(this.state)){
            var validate = this.state.validate.shareRatio;
            if (!Functions.isEmptyObject(validate)) {
                if (!validate.validation) {
                    className += ' error';
                    hint = <span className="text-red">{validate.hint}</span>;
                }
            }
        }

        return <FormInput label='出让股份'
                          name='shareRatio'
                          value={this.props.data}
                          className= {className}
                          onChange={this.change}
                          onBlur={this.blur}
                          hint= {hint}
            />
    },

    change(e){
        if(this.props.investment.trim()==''){
            ValidateActions.remindInvestment();
            return;
        }
        ValidateActions.shareRatio(e.target.name,e.target.value);
        this.props.onChange(e);
    },
    blur(e){
        var validate = this.state.validate.shareRatio;
        if (e.target.value.trim()!=''&&!validate.validation) {
            e.target.focus();
        }
    }

});


module.exports = ShareRatio;