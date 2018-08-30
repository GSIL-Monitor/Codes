var React = require('react');

var FormInput = React.createClass({

    render(){
        var require;
        if(this.props.required){
            require = <span className='left-required'>*</span>
        }
        var percent;
        if(this.props.name=='shareRatio'){
            percent=<span className='cc-percent'>%</span>
        }
        var className = "cc-form-left";
        if(this.props.admin){
            className+=" cc-org-left";
        }
        if(this.props.user){
            className+=" org-user-left";
        }
        var util;
        if(this.props.unit){
             util = <span className="text-red">（单位:万）</span>
        }
        return (

            <div className="create-company-form">

                <div className={className}>
                    {require}
                    <span>{this.props.label}</span>
                </div>

                <div className="cc-form-right">
                    <div className="form-input">
                        <input type="text"
                               className={this.props.className}
                               name={this.props.name}
                               value={this.props.value}
                               placeholder={this.props.placeholder}
                               onChange={this.change}
                               onBlur={this.blur}
                               id={this.props.id}
                            />
                        {util}
                    </div>
                    {percent}

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

module.exports = FormInput;
