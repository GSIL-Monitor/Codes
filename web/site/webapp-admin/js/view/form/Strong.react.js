var React = require('react');

var Strong = React.createClass({

    render: function() {
        return (
            <div className="form-part">
                <label>
                    {this.props.name}
                </label>

                <strong>
                    {this.props.value}
                </strong>
            </div>
        );
    }
});

module.exports = Strong;
