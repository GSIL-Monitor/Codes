var React = require('react');
var ReactPropTypes = React.PropTypes;

var Select = require('./Select.react');

var FormSelect = React.createClass({

    //propTypes: {
    //    label: ReactPropTypes.string,
    //    name:ReactPropTypes.string,
    //    select: ReactPropTypes.array
    //},

    render: function() {
        return (
            <div className="form-part">
                <label>{this.props.label}</label>
                <Select name={this.props.name}
                        value={this.props.value}
                        select={this.props.select}
                        onChange={this.props.onChange}
                    />
            </div>
        );
    }
});

module.exports = FormSelect;
