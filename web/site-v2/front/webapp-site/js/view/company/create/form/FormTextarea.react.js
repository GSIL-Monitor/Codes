/**
 * Created by haiming on 16/2/3.
 */
var React = require('react');

var FormTextarea = React.createClass({

    render(){
        var require;
        if(this.props.required){
            require = <span className='left-required'>*</span>
        }

        return (

            <div className="create-company-form">

                <div className='cc-form-left'>
                    {require}
                    <span>{this.props.label}</span>
                </div>

                <div className="cc-form-right">
                    <div className="form-input">
                        <textarea type="text"
                               className={this.props.className}
                               name={this.props.name}
                               value={this.props.value}
                               placeholder={this.props.placeholder}
                               onChange={this.change}
                               onBlur={this.blur}
                            />
                    </div>

                    <div className="form-hint">
                        {this.props.hint}
                    </div>
                </div>
            </div>
        );
    },

    change(e){
        this.props.onChange(e);
    },
    blur(e){
        if(this.props.onBlur != null)
            this.props.onBlur(e);
    }
});

module.exports = FormTextarea;
