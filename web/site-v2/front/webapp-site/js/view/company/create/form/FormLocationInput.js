var React = require('react');
var LocationInput = require('../../../../../../react-kit/basic/search/LocationInput.react');
var FormLocationInput = React.createClass({

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
                        <LocationInput  name={this.props.name}
                                        value={this.props.value}
                                        from={this.props.from}
                                        className={this.props.className}
                                        type={this.props.type}
                                        id={this.props.id}

                            />
                    </div>
                    <div className="form-hint">
                        {this.props.hint}
                    </div>
                </div>
            </div>
        );
    },
});

module.exports = FormLocationInput;
