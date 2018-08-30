var React = require('react');
var ReactPropTypes = React.PropTypes;
var Required=  require('../util/Required')

var InputText = React.createClass({

    //propTypes: {
    //    className: ReactPropTypes.string,
    //    id: ReactPropTypes.string,
    //    name: ReactPropTypes.string,
    //    value: ReactPropTypes.string,
    //    placeholder: ReactPropTypes.string
    //},

    getInitialState: function() {
        return {
            name: this.props.value || ''
        };
    },

    render: function() {
        var onBlur = this.props.onBlur?this.handleBlur:"";

            return (
                <input type="text"
                       className={this.props.className}
                       id={this.props.id}
                       name={this.props.name}
                       value={this.props.value}
                       placeholder={this.props.placeholder}
                       onChange={this.handleChange}
                       onBlur={onBlur}
                    />
            );
    },

    handleChange: function(event) {
        this.props.onChange(event);
    },
    handleBlur:function(event){
        this.props.onBlur(event);
    },
});

module.exports = InputText;
