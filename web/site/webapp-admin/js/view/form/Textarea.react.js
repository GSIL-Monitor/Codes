var React = require('react');
var ReactPropTypes = React.PropTypes;

var Textarea = React.createClass({

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
        //console.log(this.props.name + ":" + this.props.value);
        return (
            <textarea
                   className={this.props.className}
                   id = {this.props.id}
                   name = {this.props.name}
                   value={this.props.value}
                   onChange={this.handleChange}
                />
        );
    },

    handleChange: function(event) {
        this.props.onChange(event);
    }

});

module.exports = Textarea;
