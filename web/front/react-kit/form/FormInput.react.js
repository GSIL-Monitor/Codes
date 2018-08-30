var React = require('react');
var ReactPropTypes = React.PropTypes;

var InputText = require('./InputText.react');

var FormInput = React.createClass({

    //propTypes: {
    //    label: ReactPropTypes.string,
    //    className: ReactPropTypes.string,
    //    id: ReactPropTypes.string,
    //    name:ReactPropTypes.string,
    //    value: ReactPropTypes.string,
    //    placeholder: ReactPropTypes.string
    //},

    render: function() {
        return (
            <div className="form-part">
                <label>{this.props.label}</label>
                <InputText  id={this.props.id}
                            name={this.props.name}
                            value={this.props.value}
                            placeholder={this.props.placeholder}
                            className={this.props.className}
                            onChange={this.props.onChange}
                        />
            </div>
        );
    }
});

module.exports = FormInput;
