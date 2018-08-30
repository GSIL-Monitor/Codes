var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ValidateActions = require('../../../../action/validation/ValidateDemodayActions');
var ValidateStore = require('../../../../store/validation/ValidateDemodayStore');
var Functions = require('../../../../../../react-kit/util/Functions');

const FormUpdateDemoday = React.createClass({
    mixins: [Reflux.connect(ValidateStore, 'validate')],
    render(){

        var hint="";
        var className= this.props.className;
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

        return (
            <div className="admin-demoday-row">
                <div ><span> {this.props.label}:</span></div>
                <div >
                    <input type="text"    className={this.props.className}
                                          name={this.props.name}
                                          value={this.props.value}
                                          onChange={this.change}
                                          onBlur={this.blur}
                    />
                    <span>
                        {hint}
                    </span>
                </div>
            </div>
        )
    },
    change(e){
        ValidateActions.change(e.target.name);
        this.props.onChange(e);
    },

    blur(e){
        if(e.target.value===this.props.oldName)return;
        ValidateActions.name(e.target.value);
    }
});


module.exports = FormUpdateDemoday;