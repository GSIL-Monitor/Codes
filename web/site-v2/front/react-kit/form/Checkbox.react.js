var React = require('react');
var ReactPropTypes = React.PropTypes;
var Required=  require('../util/Required')

var Checkbox = React.createClass({

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
        return (
            <label>
            <input type="checkbox"
                   name={this.props.name}
                   value={this.props.value}
                   onChange={this.handleChange}
                />
                {this.props.cnName}
           </label>
        );
    },

    handleChange: function(event) {
        this.props.onChange(event);
    },
});

module.exports = Checkbox;
